# ServiceAccount in chatapp namespace
apiVersion: v1
kind: ServiceAccount
metadata:
  name: {{ .Release.Name }}-secret-manager-sa
  namespace: {{ include "chat.app.namespace" . }}
  annotations:
    argocd.argoproj.io/sync-wave: "-3"
---
# Role in mysql namespace allowing read access to secrets
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: {{ .Release.Name }}-mysql-secret-reader
  namespace: {{ include "chat.app.mysql.namespace" . }}
  annotations:
    argocd.argoproj.io/sync-wave: "-3"
rules:
  - apiGroups: [""]
    resources: ["secrets"]
    verbs: ["get"]
---
# RoleBinding in mysql namespace binding secret-manager-sa from chatapp to mysql-secret-reader
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: {{ .Release.Name }}-allow-chatapp-to-read-mysql-secrets
  namespace: {{ include "chat.app.mysql.namespace" . }}
  annotations:
    argocd.argoproj.io/sync-wave: "-3"
subjects:
  - kind: ServiceAccount
    name: {{ .Release.Name }}-secret-manager-sa
    namespace: {{ include "chat.app.namespace" . }}
roleRef:
  kind: Role
  name: {{ .Release.Name }}-mysql-secret-reader
  apiGroup: rbac.authorization.k8s.io
---
# Role in chatapp namespace allowing write access to secrets
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: {{ .Release.Name }}-chat-secret-writer
  namespace: {{ include "chat.app.namespace" . }}
  annotations:
    argocd.argoproj.io/sync-wave: "-3"
rules:
  - apiGroups: [""]
    resources: ["secrets"]
    verbs: ["get", "create", "update", "patch"]
---
# RoleBinding in chatapp namespace binding secret-manager-sa to chatapp-secret-writer
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: {{ .Release.Name }}-bind-chatapp-secret-writer
  namespace: {{ include "chat.app.namespace" . }}
  annotations:
    argocd.argoproj.io/sync-wave: "-3"
subjects:
  - kind: ServiceAccount
    name: {{ .Release.Name }}-secret-manager-sa
    namespace: {{ include "chat.app.namespace" . }}
roleRef:
  kind: Role
  name: {{ .Release.Name }}-chat-secret-writer
  apiGroup: rbac.authorization.k8s.io