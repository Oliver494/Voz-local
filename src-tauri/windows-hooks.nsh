; Microsoft installer elevates itself when needed. Do not disable Windows protections.
!macro NSIS_HOOK_POSTINSTALL
  ExecWait '"$INSTDIR\resources\tools\vc_redist.x64.exe" /install /passive /norestart' $0
  ${If} $0 == 3010
    SetRebootFlag true
  ${ElseIf} $0 != 0
    ${If} $0 != 1638
      MessageBox MB_ICONEXCLAMATION "Microsoft Visual C++ runtime setup returned $0. Voice engine setup may need a Windows restart or repair."
    ${EndIf}
  ${EndIf}
!macroend
