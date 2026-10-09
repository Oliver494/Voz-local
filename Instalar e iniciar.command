#!/bin/bash
cd "$(dirname "$0")" || exit 1
bash instalar-e-iniciar.sh
voz_exit=$?
if [[ $voz_exit -ne 0 ]]; then
  echo "Installation failed / No se pudo completar. Pulsa Intro para cerrar."
  read -r
fi
exit "$voz_exit"
