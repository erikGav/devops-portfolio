apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: {{ .Release.Name }}-chatapp-monitor
  namespace: monitoring
  labels:
    {{- toYaml (merge (include "chat.app.labels" . | fromYaml) (dict "tier" "monitoring") .Values.prometheusSelector) | nindent 4 }}
spec:
  selector:
    matchLabels:
      {{- toYaml (merge (include "chat.app.labels" . | fromYaml) (dict "tier" "ip")) | nindent 6 }}
  endpoints:
    - port: chat-port 
      path: /metrics
      interval: 30s
      scrapeTimeout: 10s
      honorLabels: false
  namespaceSelector:
    matchNames:
      - {{ include "chat.app.namespace" . }}
