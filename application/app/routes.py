from flask import request, jsonify, render_template, current_app
from models import Chat
from datetime import datetime, timezone, timedelta
from sqlalchemy import func, distinct
import csv
import os


# Implemented by Erik
NOW = datetime.now(timezone.utc)

def safe_log(level, message, **kwargs):
    """Safely log with structured data, falling back to simple logging"""
    try:
        if hasattr(current_app, 'logger'):
            logger = current_app.logger
            if hasattr(logger, level.lower()):
                getattr(logger, level.lower())(message, **kwargs)
                return
    except:
        pass
    
    # Fallback to print for tests or when structured logging fails
    if kwargs:
        print(f"{level}: {message} - {kwargs}")
    else:
        print(f"{level}: {message}")


def register_routes(app, db):

    @app.route('/api/chat/<room>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def chat(room):
        if request.method == 'POST':
            # Send new message
            username = request.form.get('username')
            message = request.form.get('msg')
            
            if not username or not message:
                safe_log("WARNING", "Message post failed - missing required fields",
                        room=room, username=username, has_message=bool(message))
                return jsonify({"error": "Username and message are required"}), 400

            chat_entry = Chat(
                room=room,
                date=NOW.strftime('%Y-%m-%d'),
                time=NOW.strftime('%H:%M:%S'),
                username=username,
                message=message,
            )

            try:
                db.session.add(chat_entry)
                db.session.commit()

                # Update Prometheus metrics
                current_app.metrics['messages_sent'].labels(room=room).inc()
                current_app.metrics['message_length'].observe(len(message))
                
                # Update gauges with current totals
                update_gauges()

                safe_log("INFO", "New message posted successfully",
                        room=room, username=username, 
                        message_length=len(message),
                        message_id=chat_entry.id)

                return jsonify(chat_entry.to_dict()), 201
                
            except Exception as e:
                db.session.rollback()
                safe_log("ERROR", "Failed to save message to database",
                        room=room, username=username, error=str(e))
                return jsonify({"error": "Failed to save message"}), 500

        elif request.method == 'GET':
            # Get all messages in room
            try:
                chat_entries = db.session.execute(
                    db.select(Chat).filter_by(room=room)).scalars().all()
                
                safe_log("INFO", "Retrieved messages for room",
                        room=room, message_count=len(chat_entries))
                
                chat_data = "\n".join(
                    f"[{entry.date} {entry.time}] {entry.username}: {entry.message}"
                    for entry in chat_entries
                )
                return chat_data
                
            except Exception as e:
                safe_log("ERROR", "Failed to retrieve messages",
                        room=room, error=str(e))
                return jsonify({"error": "Failed to retrieve messages"}), 500
            
        elif request.method == 'PUT':
            # Update username
            old_username = request.form.get('old_username')
            new_username = request.form.get('new_username')
        
            if not old_username or not new_username:
                safe_log("WARNING", "Username update failed - missing parameters",
                        room=room, has_old_username=bool(old_username),
                        has_new_username=bool(new_username))
                return jsonify({"error": "Both old_username and new_username are required"}), 400
            
            if old_username == new_username:
                safe_log("WARNING", "Username update failed - same username provided",
                        room=room, username=old_username)
                return jsonify({"error": "New username must be different from current username"}), 400
        
            # Check if new username is already taken in this room
            existing_user = db.session.execute(
                db.select(Chat).filter_by(room=room, username=new_username)
            ).scalar_one_or_none()
            
            if existing_user:
                safe_log("WARNING", "Username update failed - username already exists",
                        room=room, old_username=old_username,
                        new_username=new_username)
                return jsonify({"error": "Username already exists in this room"}), 400
        
            # Update all messages from the old username to new username in this room
            try:
                updated_count = db.session.execute(
                    db.update(Chat)
                    .where(Chat.room == room, Chat.username == old_username)
                    .values(username=new_username)
                ).rowcount
                
                db.session.commit()
                
                if updated_count == 0:
                    safe_log("WARNING", "Username update failed - no messages found",
                            room=room, old_username=old_username)
                    return jsonify({"error": "No messages found for this username in this room"}), 404
                
                # Update Prometheus metrics
                current_app.metrics['username_changes'].inc()
                update_gauges()
                
                safe_log("INFO", "Username updated successfully",
                        room=room, old_username=old_username,
                        new_username=new_username,
                        messages_updated=updated_count)
                    
                return jsonify({
                    "message": f"Username updated successfully. {updated_count} messages updated.",
                    "old_username": old_username,
                    "new_username": new_username,
                    "messages_updated": updated_count
                }), 200
                
            except Exception as e:
                db.session.rollback()
                current_app.metrics['database_connection'].set(0)
                safe_log("ERROR", "Username update failed - database error",
                        room=room, old_username=old_username,
                        new_username=new_username, error=str(e))
                return jsonify({"error": "Failed to update username"}), 500
                
        elif request.method == 'DELETE':
            # Clear all messages in room
            try:
                deleted_count = db.session.query(Chat).filter_by(room=room).delete()
                db.session.commit()
                
                # Update Prometheus metrics
                current_app.metrics['chat_clears'].labels(room=room).inc()
                update_gauges()
                
                safe_log("INFO", "Chat history cleared",
                        room=room, messages_deleted=deleted_count)
                
                return jsonify({
                    "message": f"Chat history deleted. {deleted_count} messages removed."
                }), 200
            except Exception as e:
                db.session.rollback()
                current_app.metrics['database_connection'].set(0)
                safe_log("ERROR", "Failed to clear chat history",
                        room=room, error=str(e))
                return jsonify({"error": "Failed to delete chat history"}), 500

    @app.route('/health', methods=['GET'])
    def health_check():
        """Simple health check endpoint for monitoring"""
        try:
            # Test database connection with a simple query
            db.session.execute(db.text('SELECT 1'))
            current_app.metrics['database_connection'].set(1)
            
            safe_log("INFO", "Health check passed", status="healthy")
            
            return jsonify({
                "status": "healthy",
                "database": "connected",
                "timestamp": NOW.strftime('%Y-%m-%d %H:%M:%S UTC'),
                "service": "chatapp"
            }), 200
            
        except Exception as e:
            current_app.metrics['database_connection'].set(0)
            safe_log("ERROR", "Health check failed", 
                    status="unhealthy", error=str(e))
            return jsonify({
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
                "timestamp": NOW.strftime('%Y-%m-%d %H:%M:%S UTC'),
                "service": "chatapp"
            }), 503

    def update_gauges():
        """Update Prometheus gauge metrics with current database state"""
        try:
            # Update room count
            room_count = db.session.execute(
                db.select(func.count(distinct(Chat.room)))
            ).scalar()
            current_app.metrics['active_rooms'].set(room_count)
            
            # Update user count
            user_count = db.session.execute(
                db.select(func.count(distinct(Chat.username)))
            ).scalar()
            current_app.metrics['total_users'].set(user_count)
            
            # Update messages today
            today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
            today_count = db.session.execute(
                db.select(func.count(Chat.id)).filter_by(date=today)
            ).scalar()
            current_app.metrics['messages_today'].set(today_count)
            
            # Ensure database connection is marked as good
            current_app.metrics['database_connection'].set(1)
            
            safe_log("DEBUG", "Metrics updated successfully",
                    room_count=room_count, user_count=user_count,
                    messages_today=today_count)
            
        except Exception as e:
            safe_log("ERROR", "Failed to update gauges", error=str(e))
            current_app.metrics['database_connection'].set(0)

    # JSON metrics endpoint for compatibility with web viewer
    @app.route('/metrics/json', methods=['GET'])
    def metrics_json():
        """JSON metrics endpoint compatible with the web viewer"""
        try:
            now = datetime.now(timezone.utc)
            today = now.strftime('%Y-%m-%d')
            
            # Basic counts
            total_messages = db.session.execute(
                db.select(func.count(Chat.id))
            ).scalar()
            
            total_rooms = db.session.execute(
                db.select(func.count(distinct(Chat.room)))
            ).scalar()
            
            total_users = db.session.execute(
                db.select(func.count(distinct(Chat.username)))
            ).scalar()
            
            # Today's activity
            messages_today = db.session.execute(
                db.select(func.count(Chat.id)).filter_by(date=today)
            ).scalar()
            
            active_users_today = db.session.execute(
                db.select(func.count(distinct(Chat.username))).filter_by(date=today)
            ).scalar()
            
            # Top 5 most active rooms
            top_rooms = db.session.execute(
                db.select(Chat.room, func.count(Chat.id).label('message_count'))
                .group_by(Chat.room)
                .order_by(func.count(Chat.id).desc())
                .limit(5)
            ).all()
            
            # Top 5 most active users
            top_users = db.session.execute(
                db.select(Chat.username, func.count(Chat.id).label('message_count'))
                .group_by(Chat.username)
                .order_by(func.count(Chat.id).desc())
                .limit(5)
            ).all()
            
            # Recent activity (last 7 days)
            seven_days_ago = (now - timedelta(days=7)).strftime('%Y-%m-%d')
            recent_messages = db.session.execute(
                db.select(func.count(Chat.id))
                .where(Chat.date >= seven_days_ago)
            ).scalar()
            
            # Average messages per room
            avg_messages_per_room = round(total_messages / max(total_rooms, 1), 2)
            
            # Average messages per user
            avg_messages_per_user = round(total_messages / max(total_users, 1), 2)
            
            safe_log("INFO", "Metrics endpoint accessed",
                    total_messages=total_messages,
                    total_rooms=total_rooms,
                    total_users=total_users)
            
            metrics_data = {
                "timestamp": now.isoformat(),
                "system_health": {
                    "database_status": "connected",
                    "total_records": total_messages
                },
                "usage_stats": {
                    "total_messages": total_messages,
                    "total_rooms": total_rooms,
                    "total_users": total_users,
                    "messages_today": messages_today,
                    "active_users_today": active_users_today,
                    "recent_messages_7d": recent_messages,
                    "avg_messages_per_room": avg_messages_per_room,
                    "avg_messages_per_user": avg_messages_per_user
                },
                "top_rooms": [
                    {"room": room, "message_count": count} 
                    for room, count in top_rooms
                ],
                "top_users": [
                    {"username": user, "message_count": count} 
                    for user, count in top_users
                ]
            }
            
            return jsonify(metrics_data), 200
            
        except Exception as e:
            safe_log("ERROR", "Metrics endpoint failed", error=str(e))
            return jsonify({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "system_health": {
                    "database_status": "error",
                    "error": str(e)
                },
                "usage_stats": {},
                "top_rooms": [],
                "top_users": []
            }), 500