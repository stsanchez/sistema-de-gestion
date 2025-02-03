# Importar el módulo de Active Directory
 Import-Module ActiveDirectory

 # Especificar la ruta donde quieres guardar el archivo
 $rutaArchivo = "C:\Users\SSanchez\Documents\Workspace\Formulario_Entrega\form_devices\reporte_formulario\static\usuarios_ad.txt"

 # Especificar la ruta de la OU deseada
 $ouPath = "OU=EMER Usuarios,OU=Usuarios,OU=EMER,DC=Emer,DC=local"

 # Obtener todos los usuarios activos que no terminen con "_SMB" y estén en la OU especificada, ordenarlos por fecha de alta y guardar solo sus nombres de usuario en un archivo de texto en la ruta especificada
 Get-ADUser -Filter {Enabled -eq $true -and SamAccountName -notlike "*_SMB"} -SearchBase $ouPath | Sort-Object whenCreated | Select-Object -ExpandProperty SamAccountName | Out-File -FilePath $rutaArchivo