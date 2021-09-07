try {
  Get-Datedf
}
catch {
  throw $_.Exception.Message
}
