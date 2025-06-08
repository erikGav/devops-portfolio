apiVersion: batch/v1
kind: Job
metadata:
  name: {{ .Release.Name }}-generate-mysql-uri
  namespace: {{ include "chat.app.namespace" . }}
  annotations:
    # "helm.sh/hook": pre-install,pre-upgrade
    # "helm.sh/hook-weight": "-1"
    argocd.argoproj.io/sync-wave: "-2"

spec:
  template:
    spec:
      restartPolicy: OnFailure
      serviceAccountName: {{ .Release.Name }}-secret-manager-sa
      containers:
        - name: {{ .Release.Name }}-generator
          image: bitnami/kubectl:latest
          command:
            - /bin/sh
            - -c
            - |
              set -e

              echo "Waiting for secret {{ .Values.mysql.auth.existingSecret }} to exist..."
              until kubectl get secret -n {{ include "chat.app.mysql.namespace" . }} {{ .Values.mysql.auth.existingSecret }} > /dev/null 2>&1; do
                echo "Still waiting for secret..."
                sleep 2
              done

              USERNAME={{ .Values.mysql.auth.username | quote }}
              PASSWORD=$(kubectl get secret -n {{ include "chat.app.mysql.namespace" . }} {{ .Values.mysql.auth.existingSecret}} -o=jsonpath='{.data.mysql-password}' | base64 -d)
              DATABASE={{ .Values.mysql.auth.database | quote }}
              MYSQL_HOST={{ .Release.Name }}-mysql-primary-headless.{{ include "chat.app.mysql.namespace" . }}.svc.cluster.local
              MYSQL_PORT=3306

              MYSQL_URI="${USERNAME}:${PASSWORD}@${MYSQL_HOST}:${MYSQL_PORT}/${DATABASE}"

              kubectl create secret -n {{ include "chat.app.namespace" . }} generic {{ .Release.Name }}-mysql-uri \
                --from-literal=MYSQL_URI="$MYSQL_URI" \
                --dry-run=client -o yaml | kubectl apply -f -