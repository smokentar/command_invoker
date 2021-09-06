try {
  Write-Host "Test"
}
catch {
  throw $_.Exception.Message
}
