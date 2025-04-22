{{/*
Expand the name of the chart.
*/}}
{{- define "revo.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "revo.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "revo.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "revo.labels" -}}
helm.sh/chart: {{ include "revo.chart" . }}
{{ include "revo.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "revo.selectorLabels" -}}
app.kubernetes.io/name: {{ include "revo.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "revo.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "revo.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{- define "revo.db.username" -}}
{{- if .Values.db.username }}
{{- .Values.db.username }}
{{- else }}
{{- $secretObj := (lookup "v1" "Secret" .Release.Namespace "revo.revo-db.credentials.postgresql.acid.zalan.do") | default dict }}
{{- $secretData := (get $secretObj "data") | default dict }}
{{- (get $secretData "username" | b64dec) | required "revo db credentials secret username is missing" }}
{{- end }}
{{- end }}

{{- define "revo.db.password" -}}
{{- if .Values.db.password }}
{{- .Values.db.password }}
{{- else }}
{{- $secretObj := (lookup "v1" "Secret" .Release.Namespace "revo.revo-db.credentials.postgresql.acid.zalan.do") | default dict }}
{{- $secretData := (get $secretObj "data") | default dict }}
{{- (get $secretData "password" | b64dec) | required "revo db credentials secret password is missing" }}
{{- end }}
{{- end }}

{{- define "revo.db.address" -}}
{{- .Values.db.address | required "revo.db.address is required" }}
{{- end }}

{{- define "revo.db.port" -}}
{{- .Values.db.port | required "revo.db.port is required" }}
{{- end }}

{{- define "revo.db.name" -}}
{{- .Values.db.name | required "revo.db.name is required" }}
{{- end }}