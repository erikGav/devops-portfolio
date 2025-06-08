{{- if .Values.mysql.namespaceOverride }}
apiVersion: v1
kind: Namespace
metadata:
  name: {{ include "chat.app.mysql.namespace" . }}
  annotations:
    # "helm.sh/hook": pre-install,pre-upgrade
    # "helm.sh/hook-weight": "-5"
    argocd.argoproj.io/sync-wave: "-5"
{{- end }}
---
{{- if  .Values.namespaceOverride }}
apiVersion: v1
kind: Namespace
metadata:
  name: {{ include "chat.app.namespace" . }}
  annotations:
    # "helm.sh/hook": pre-install,pre-upgrade
    # "helm.sh/hook-weight": "-5"
    argocd.argoproj.io/sync-wave: "-5"
{{- end }}