{{- $labels := include "chat.app.labels" . | fromYaml }}
{{- $merged := merge $labels (dict "tier" "app") }}

apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    {{- toYaml $merged | nindent 4 }}
  name: {{ .Release.Name }}-chat-app
  namespace: {{ include "chat.app.namespace" . }}
  annotations:
    argocd.argoproj.io/sync-wave: "3"
spec:
  replicas: {{ .Values.replicaCount | default 2 }}
  selector:
    matchLabels:
      {{- toYaml $merged | nindent 6 }}
  {{- if .Values.strategy }}
  strategy: 
    type: {{ .Values.strategy.type | quote }}
    {{- if eq (lower .Values.strategy.type) "rollingupdate" }}
    rollingUpdate:
      maxUnavailable: {{ default "25%" .Values.strategy.rollingUpdate.maxUnavailable | quote }}
      maxSurge: {{ default "50%" .Values.strategy.rollingUpdate.maxSurge | quote }}
    {{- end }}
  {{- end }}
  template:
    metadata:
      labels:
        {{- toYaml $merged | nindent 8 }}
    spec:
      containers:
      - image: 793786247026.dkr.ecr.ap-south-1.amazonaws.com/erik/chat-app:{{ .Values.appVersion | default "latest" }}
        name: {{ .Release.Name }}-app
        imagePullPolicy: IfNotPresent
        envFrom:
        - secretRef:
            name: {{ .Release.Name }}-mysql-uri
        ports:
        - containerPort: 5000
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 5
          successThreshold: 2
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 5
          successThreshold: 1
        resources: 
          {{- include "chat.app.resources" . }}
status: {}
