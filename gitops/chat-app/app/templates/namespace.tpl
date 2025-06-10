{{- if .Values.mysql.namespaceOverride }}
apiVersion: v1
kind: Namespace
metadata:
  name: {{ include "chat.app.mysql.namespace" . }}
  annotations:
    argocd.argoproj.io/sync-wave: "-5"
{{- end }}
---
{{- if  .Values.namespaceOverride }}
apiVersion: v1
kind: Namespace
metadata:
  name: {{ include "chat.app.namespace" . }}
  annotations:
    argocd.argoproj.io/sync-wave: "-5"
{{- end }}