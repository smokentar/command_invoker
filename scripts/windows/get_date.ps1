try {
  Get-Date
}
catch {
  throw $_.Exception.Message
}
