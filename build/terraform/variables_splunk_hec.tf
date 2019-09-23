variable "SPLUNK_HEC_TOKEN" {
  description = "Splunk HEC Token"
  type        = "string"
}

variable "SPLUNK_HEC_URL" {
  description = "Splunk HEC Endpoint"
  type        = "string"
}

variable "SPLUNK_HEC_TIMEOUT" {
  description = "Splunk HEC Sending/POST Timeout"
  type        = "string"
  default     = "30"
}

variable "SPLUNK_HEC_INDEX" {
  description = "Splunk HEC Index"
  type        = "string"
}

variable "SPLUNK_HEC_SOURCETYPE" {
  description = "Splunk HEC Source Type"
  type        = "string"
}
