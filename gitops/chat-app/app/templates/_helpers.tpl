{{- define "chat.app.labels" -}}
    {{- $labels := dict "app" .Release.Name }}
    {{- if .Values.customLabels }}
        {{- $labels = merge $labels .Values.customLabels }}
    {{- end }}
    {{- toYaml $labels }}
{{- end }}

{{- define "chat.app.namespace" -}}
    {{- if .Values.namespaceOverride }}
        {{- print .Values.namespaceOverride }}
    {{- else }}
        {{- print .Release.Namespace }}
    {{- end }}
{{- end }}

{{- define "chat.app.mysql.namespace" -}}
    {{- if .Values.mysql.namespaceOverride }}
        {{- print .Values.mysql.namespaceOverride }}
    {{- else }}
        {{- print .Release.Namespace }}
    {{- end }}
{{- end }}

{{- define "chat.app.resources" -}}
    {{- if .Values.resources }}
        {{- toYaml .Values.resources | nindent 12 }}
    {{- else }}
      {{- toYaml (dict
        "limits" (dict "cpu" "1" "memory" "512Mi")
        "requests" (dict "cpu" "250m" "memory" "256Mi")
      ) | nindent 12 }}
    {{- end }}
{{- end }}