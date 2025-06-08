apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ .Release.Name }}-ingress
  namespace: {{ include "chat.app.namespace" . }}
  {{- if .Values.ingress.annotations }}
  annotations: {{- toYaml .Values.ingress.annotations | nindent 4 }}
  {{- end }}
spec:
  {{- if .Values.ingress.tls.enabled }}
  tls:
    - hosts: {{- toYaml .Values.ingress.tls.hosts | nindent 8 }}
      secretName: {{ .Release.Name }}-tls
  {{- end }}
  ingressClassName: nginx
  rules:
    - host: {{ .Values.ingress.host | quote }}
      http:
        paths:
          - path: {{ .Values.ingress.path | quote }}
            pathType: Prefix
            backend:
              service:
                name: {{ .Release.Name }}-svc
                port:
                  number: {{ .Values.appPort }}
    {{- range .Values.ingress.additionalPaths }}
    - host: {{ . | quote }}
      http:
        paths:
          - path: {{ $.Values.ingress.path | quote }}
            pathType: Prefix
            backend:
              service:
                name: {{ $.Release.Name }}-svc
                port:
                  number: {{ $.Values.appPort }}
    {{- end }}