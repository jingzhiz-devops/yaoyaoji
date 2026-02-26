{{/*
Expand the name of the chart.
*/}}
{{- define "yaoyaoji.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "yaoyaoji.fullname" -}}
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
{{- define "yaoyaoji.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "yaoyaoji.labels" -}}
helm.sh/chart: {{ include "yaoyaoji.chart" . }}
{{ include "yaoyaoji.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "yaoyaoji.selectorLabels" -}}
app.kubernetes.io/name: {{ include "yaoyaoji.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
MySQL labels
*/}}
{{- define "yaoyaoji.mysql.labels" -}}
{{ include "yaoyaoji.labels" . }}
app: mysql
{{- end }}

{{/*
Backend labels
*/}}
{{- define "yaoyaoji.backend.labels" -}}
{{ include "yaoyaoji.labels" . }}
app: backend
{{- end }}

{{/*
Frontend labels
*/}}
{{- define "yaoyaoji.frontend.labels" -}}
{{ include "yaoyaoji.labels" . }}
app: frontend
{{- end }}
