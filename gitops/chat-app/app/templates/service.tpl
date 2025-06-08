apiVersion: v1
kind: Service
metadata:
  labels:
    {{- toYaml (merge (include "chat.app.labels" . | fromYaml) (dict "tier" "ip")) | nindent 4 }}
  name: {{ .Release.Name }}-svc
  namespace: {{ include "chat.app.namespace" . }}
spec:
  ports:
    - name: chat-port
      port: {{ .Values.appPort }}
      protocol: TCP
      targetPort: 5000
  selector:
    {{- toYaml (merge (include "chat.app.labels" . | fromYaml) (dict "tier" "app")) | nindent 4 }}
  type: ClusterIP