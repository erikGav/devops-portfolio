{{- $labels := include "chat.app.labels" . | fromYaml }}
{{- $merged := merge $labels (dict "tier" "externalSecret") }}

apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: {{ .Release.Name }}-db-external-secrets
  namespace: {{ include "chat.app.mysql.namespace" . }}
  annotations:
    argocd.argoproj.io/sync-wave: "-4"
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager-cluster
    kind: ClusterSecretStore
  target:
    name: {{ .Values.mysql.auth.existingSecret }}
    creationPolicy: Owner
    template:
      metadata:
        labels: 
          {{- toYaml $merged | nindent 12 }}
      type: Opaque
  data:
    - secretKey: mysql-password
      remoteRef:
        key: erik-chatapp/mysql
        property: mysql-password
    - secretKey: mysql-root-password
      remoteRef:
        key: erik-chatapp/mysql
        property: mysql-root-password
    - secretKey: mysql-replication-password
      remoteRef:
        key: erik-chatapp/mysql
        property: mysql-replication-password
        
        
                    