const $ = (id) => document.getElementById(id);
const translations = {
  en: {
    workspace:"WORKSPACE", textToSpeech:"Text to speech", myVoices:"My voices", projects:"Projects", allOnYourComputer:"Everything on your computer", localVoicesAndProjects:"Local voices and projects", voiceStudio:"VOICE STUDIO", language:"Language", checkingGpu:"Checking GPU…", checkingQwen:"Checking Qwen3-TTS…", voiceLibrary:"VOICE LIBRARY", myVoicesTitle:"My voices", saveSampleForProjects:"Save a sample to use it in all your projects.", localModel:"LOCAL MODEL", checkingLocalInstallation:"Checking local installation…", checking:"Checking…", addVoice:"Add voice", profileName:"Profile name", exactSampleText:"Exact sample text", samplePlaceholder:"Write exactly what you are going to record or what can already be heard in the audio.", sampleHelp:"The text must match everything you say exactly. Record in a quiet place; a 3 to 5 second sample usually works well.", recordSample:"● Record sample", stop:"■ Stop", uploadAudio:"Or upload an audio file", saveVoice:"Save voice", savedVoices:"Saved voices", profilesEmpty:"Your profiles will appear here.", createAudio:"CREATE AUDIO", textToSpeechTitle:"Text to speech", writeScriptChooseVoice:"Write your script, choose a voice and generate your narration.", yourText:"Your text", scriptPlaceholder:"Write the narration for your next video…", ollamaHelp:"Writing help with Ollama", localModelLabel:"Local model", searchingOllama:"Searching Ollama…", improveNarration:"Improve for narration", shortenScript:"Shorten script", correctText:"Correct text", editText:"Edit text", prepareProject:"Prepare project", voice:"Voice", selectVoice:"Select a voice", addVoiceLink:"Add a voice", projectName:"Project name", projectNamePlaceholder:"E.g. Video introduction", voiceModel:"Voice model", modelQuality:"Qwen3-TTS 1.7B · Best quality", modelFast:"Qwen3-TTS 0.6B · Faster", modelEco:"Qwen3-TTS 0.6B · Eco", modelChooserHelp:"The lighter options use less VRAM and usually generate faster.", scriptGenerationMode:"How do you want to generate the script?", fragments:"By fragments", fragmentsHelp:"Edit and regenerate each part separately.", fullAudio:"Full audio", fullAudioHelp:"One script, player and file. Long text is processed in parts internally.", createProject:"Create project", yourNarrations:"YOUR NARRATIONS", projectsTitle:"Projects", playRegenerateDownload:"Play, regenerate and download your audio.", newProject:"New project", myProjects:"My projects", projectsEmpty:"No projects yet.", studioReady:"Your studio is ready", createProjectToSee:"Create a project to see its script and audio here.", currentProject:"CURRENT PROJECT", mode:"Mode", changeMode:"Change mode", generatePending:"Generate pending", downloadAudio:"Download audio", voiceSettings:"Voice settings", voiceSettingsHelp:"Model, stability, similarity, style and language", naturalSound:"↺ Natural sound", stability:"Stability", moreVariable:"More variable", moreStable:"More stable", similarity:"Similarity", timbreOnly:"Timbre only", audioAndText:"Audio and text", similarityHelp:"Audio and text uses the sample and its exact transcript to preserve speech more closely.", styleExaggeration:"Style exaggeration", none:"None", moreVariation:"More variation", styleHelp:"Adjusts variation while generating; the effect can change between fragments.", languageOverride:"Language override", languageToGenerate:"Language to generate", spanish:"Spanish", english:"English", auto:"Automatic", settingsFootnote:"Narration uses Qwen's original audio at 1.00×, without effects. To hear changes to model, stability, similarity or style, press “Regenerate”.", footerTitle:"VOZ LOCAL", footerText:"Your voice studio on this computer", gpuAvailable:"● AMD GPU available", gpuUnavailable:"● GPU unavailable", offline:"● Offline", modelInUse:"in use", modelInstalled:"installed", modelMissing:"not installed", modelFallback:"Backup in use for voice generation.", modelDescription:"Local voice model · Qwen/Qwen3-TTS-12Hz-1.7B-Base", delete:"Delete", deleteVoice:"Delete voice {name}", secondsSample:"s sample", sampleWarning:"This sample is {duration} s for {words} written words. Check that the text includes everything you say.", longSampleTip:"Long sample: if the voice sounds sped up or artificial, try another profile with 3 to 5 seconds and its exact text.", editSampleText:"Correct sample text", exactWordsHeard:"Exact words heard", saveTranscript:"Save transcript", transcriptHelp:"Include every repetition. Then generate the fragment again.", waitOperation:"Wait for the current operation to finish.", emptyChunk:"Audio pending", qwenOriginal:"Original Qwen · 1.00×", oldAudio:"Previous audio: regenerate to get the original Qwen · 1.00×", fragment:"fragment", fragmentsWord:"fragments", generated:"Generated", pending:"Pending", narrationFull:"FULL NARRATION", fragmentLabel:"FRAGMENT {n}", narrationText:"Full narration text", fragmentText:"Fragment {n} text", saveText:"Save text", regenerateAudio:"↻ Regenerate audio", generateAudio:"▶ Generate audio", regenerate:"↻ Regenerate", generate:"▶ Generate", generatedModel:"Generated · {model}", audioPending:"Audio pending", saved:"Saved", saving:"Saving…", generatingFull:"Generating the full narration. Long scripts may take several minutes…", savingGenerating:"Saving changes and generating audio…", fullNarrationGenerated:"Full narration generated. You can listen and export it.", fragmentGenerated:"Fragment generated. You can listen to it.", allHaveAudio:"All fragments already have audio.", narrationComplete:"Narration complete. You can export it as WAV or MP3.", copiedMode:"I created a copy with the selected mode to preserve the original project's audio.", modeUpdated:"Mode updated. You can now generate the audio.", exportError:"Could not export the audio.", ollamaUnavailable:"Ollama unavailable", writeScriptChooseModel:"Write a script and choose an Ollama model.", editing:"Editing…", scriptEdited:"Script edited. Review it before creating the project.", browserNoRecord:"This browser cannot record. You can upload an audio file.", sampleRecorded:"Sample recorded: {seconds} s", recording:"Recording {seconds} s", micError:"Could not access the microphone. Check permissions or upload a file.", recordOrSelect:"Record a sample or select a file.", voiceSaved:"Voice saved. You can create your first project.", completeFields:"Complete the title, voice and script.", fullProjectCreated:"Full audio project created.", projectCreated:"Project created with {count} fragments.", noConnection:"Could not query the local model status.", startupError:"Could not start the web: {error}", noVoiceProfiles:"Your profiles will appear here.", noProjects:"No projects yet.", deleteProject:"Delete project {name}", deleteVoiceConfirm:"Delete voice “{name}” and its sample?", deleteProjectConfirm:"Delete project “{name}”? Its script, fragments and generated audio will be removed. Your voice profile will be kept.", cannotUndo:"This action cannot be undone.", projectsAlsoDeleted:"{count} linked project(s) will also be deleted with their fragments and audio:", voiceDeleted:"Voice “{name}” deleted{extra}.", withProjects:" together with {count} project(s)", projectDeleted:"Project “{name}” deleted.", transcriptRequired:"Write the exact words from the sample.", transcriptSaved:"Saved. Generate again to hear the change.", transcriptSaveError:"Could not save: {error}", waitCurrent:"Wait for the current operation.", emptyFragmentError:"No fragment can be empty.", savedDrafts:"Text saved. Edited fragments are now pending generation.", saveError:"Error saving", errorPrefix:"Could not save: ", naturalSaveError:"Error saving", statusSaved:"Saved", statusSaving:"Saving…", statusOffline:"Offline"
  },
  es: {
    workspace:"ESPACIO DE TRABAJO", textToSpeech:"Texto a voz", myVoices:"Mis voces", projects:"Proyectos", allOnYourComputer:"Todo en tu equipo", localVoicesAndProjects:"Voces y proyectos locales", voiceStudio:"ESTUDIO DE VOZ", language:"Idioma", checkingGpu:"Comprobando GPU…", checkingQwen:"Comprobando Qwen3-TTS…", voiceLibrary:"BIBLIOTECA DE VOCES", myVoicesTitle:"Mis voces", saveSampleForProjects:"Guarda una muestra para usarla en todos tus proyectos.", localModel:"MODELO LOCAL", checkingLocalInstallation:"Comprobando instalación local…", checking:"Comprobando…", addVoice:"Añadir voz", profileName:"Nombre del perfil", exactSampleText:"Texto exacto de la muestra", samplePlaceholder:"Escribe aquí, palabra por palabra, lo que vas a grabar o lo que ya se oye en el audio.", sampleHelp:"El texto debe coincidir exactamente con todo lo que se oye. Graba en un lugar silencioso; una muestra de 3 a 5 segundos suele funcionar bien.", recordSample:"● Grabar muestra", stop:"■ Detener", uploadAudio:"O subir un archivo de audio", saveVoice:"Guardar voz", savedVoices:"Voces guardadas", profilesEmpty:"Tus perfiles aparecerán aquí.", createAudio:"CREAR AUDIO", textToSpeechTitle:"Texto a voz", writeScriptChooseVoice:"Escribe tu guion, elige una voz y genera tu narración.", yourText:"Tu texto", scriptPlaceholder:"Escribe aquí la narración de tu próximo vídeo…", ollamaHelp:"Ayuda para escribir con Ollama", localModelLabel:"Modelo local", searchingOllama:"Buscando Ollama…", improveNarration:"Mejorar para narración", shortenScript:"Acortar guion", correctText:"Corregir texto", editText:"Editar texto", prepareProject:"Preparar proyecto", voice:"Voz", selectVoice:"Selecciona una voz", addVoiceLink:"Añadir una voz", projectName:"Nombre del proyecto", projectNamePlaceholder:"Ej. Introducción del vídeo", voiceModel:"Modelo de voz", modelQuality:"Qwen3-TTS 1.7B · Mejor calidad", modelFast:"Qwen3-TTS 0.6B · Más rápido", modelEco:"Qwen3-TTS 0.6B · Eco", modelChooserHelp:"Las opciones ligeras usan menos VRAM y normalmente generan más rápido.", scriptGenerationMode:"Cómo quieres generar el guion", fragments:"Por fragmentos", fragmentsHelp:"Edita y regenera cada parte por separado.", fullAudio:"Audio completo", fullAudioHelp:"Un solo guion, reproductor y archivo. Los textos largos se procesan por partes internamente.", createProject:"Crear proyecto", yourNarrations:"TUS NARRACIONES", projectsTitle:"Proyectos", playRegenerateDownload:"Reproduce, regenera y descarga tus audios.", newProject:"Nuevo proyecto", myProjects:"Mis proyectos", projectsEmpty:"Todavía no hay proyectos.", studioReady:"Tu estudio está listo", createProjectToSee:"Crea un proyecto para ver aquí su guion y audio.", currentProject:"PROYECTO ACTUAL", mode:"Modo", changeMode:"Cambiar modo", generatePending:"Generar pendientes", downloadAudio:"Descargar audio", voiceSettings:"Ajustes de voz", voiceSettingsHelp:"Modelo, estabilidad, similitud, estilo e idioma", naturalSound:"↺ Sonido natural", stability:"Estabilidad", moreVariable:"Más variable", moreStable:"Más estable", similarity:"Similitud", timbreOnly:"Solo timbre", audioAndText:"Audio y texto", similarityHelp:"Audio y texto usa la muestra y su transcripción literal para conservar mejor el habla.", styleExaggeration:"Exageración de estilo", none:"Ninguno", moreVariation:"Más variación", styleHelp:"Ajusta la variación al generar; el efecto puede cambiar entre fragmentos.", languageOverride:"Anulación de idioma", languageToGenerate:"Idioma para generar", spanish:"Español", english:"Inglés", auto:"Automático", settingsFootnote:"La narración usa el audio original de Qwen a 1,00×, sin efectos. Para oír cambios de modelo, estabilidad, similitud o estilo, pulsa «Regenerar».", footerTitle:"VOZ LOCAL", footerText:"Tu estudio de voz en este equipo", gpuAvailable:"● GPU AMD disponible", gpuUnavailable:"● GPU no disponible", offline:"● Sin conexión", modelInUse:"en uso", modelInstalled:"instalado", modelMissing:"sin instalar", modelFallback:"Respaldo en uso para la generación de voz.", modelDescription:"Modelo de voz local · Qwen/Qwen3-TTS-12Hz-1.7B-Base", delete:"Eliminar", deleteVoice:"Eliminar voz {name}", secondsSample:"s de muestra", sampleWarning:"Esta muestra dura {duration} s para {words} palabras escritas. Comprueba que el texto incluye todo lo que dices.", longSampleTip:"Muestra larga: si la voz suena acelerada o artificial, prueba otro perfil con 3 a 5 segundos y su texto exacto.", editSampleText:"Corregir texto de la muestra", exactWordsHeard:"Palabras exactas que se oyen", saveTranscript:"Guardar transcripción", transcriptHelp:"Incluye todas las repeticiones. Después, genera otra vez el fragmento.", waitOperation:"Espera a que termine la operación actual.", emptyChunk:"Audio pendiente", qwenOriginal:"Original de Qwen · 1,00×", oldAudio:"Audio anterior: regenera para obtener el original de Qwen · 1,00×", fragment:"fragmento", fragmentsWord:"fragmentos", generated:"Generado", pending:"Pendiente", narrationFull:"NARRACIÓN COMPLETA", fragmentLabel:"FRAGMENTO {n}", narrationText:"Texto completo de la narración", fragmentText:"Texto del fragmento {n}", saveText:"Guardar texto", regenerateAudio:"↻ Regenerar audio", generateAudio:"▶ Generar audio", regenerate:"↻ Regenerar", generate:"▶ Generar", generatedModel:"Generado · modelo {model}", audioPending:"Audio pendiente", saved:"Guardado", saving:"Guardando…", generatingFull:"Generando la narración completa. Si el guion es largo, puede tardar varios minutos…", savingGenerating:"Guardando cambios y generando audio…", fullNarrationGenerated:"Narración completa generada. Ya puedes escucharla y exportarla.", fragmentGenerated:"Fragmento generado. Ya puedes escucharlo.", allHaveAudio:"Todos los fragmentos ya tienen audio.", narrationComplete:"Narración completa. Puedes exportarla en WAV o MP3.", copiedMode:"Creé una copia con el modo elegido para conservar los audios del proyecto original.", modeUpdated:"Modo actualizado. Ya puedes generar el audio.", exportError:"No se pudo exportar el audio.", ollamaUnavailable:"Ollama no disponible", writeScriptChooseModel:"Escribe un guion y elige un modelo de Ollama.", editing:"Editando…", scriptEdited:"Guion editado. Revísalo antes de crear el proyecto.", browserNoRecord:"Este navegador no permite grabar. Puedes subir un archivo de audio.", sampleRecorded:"Muestra grabada: {seconds} s", recording:"Grabando {seconds} s", micError:"No se pudo acceder al micrófono. Revisa sus permisos o sube un archivo.", recordOrSelect:"Graba una muestra o selecciona un archivo.", voiceSaved:"Voz guardada. Ya puedes crear tu primer proyecto.", completeFields:"Completa el título, la voz y el guion.", fullProjectCreated:"Proyecto de audio completo creado.", projectCreated:"Proyecto creado con {count} fragmentos.", noConnection:"No se pudo consultar el estado del modelo local.", startupError:"No se pudo iniciar la web: {error}", noVoiceProfiles:"Tus perfiles aparecerán aquí.", noProjects:"Todavía no hay proyectos.", deleteProject:"Eliminar proyecto {name}", deleteVoiceConfirm:"¿Eliminar la voz «{name}» y su muestra?", deleteProjectConfirm:"¿Eliminar el proyecto «{name}»? Se borrarán su guion, fragmentos y audios generados. Tu perfil de voz se conservará.", cannotUndo:"Esta acción no se puede deshacer.", projectsAlsoDeleted:"También se eliminarán {count} proyecto(s) con sus fragmentos y audios:", voiceDeleted:"Voz «{name}» eliminada{extra}.", withProjects:" junto con {count} proyecto(s)", projectDeleted:"Proyecto «{name}» eliminado.", transcriptRequired:"Escribe las palabras exactas de la muestra.", transcriptSaved:"Guardado. Genera de nuevo para escuchar el cambio.", transcriptSaveError:"No se pudo guardar: {error}", waitCurrent:"Espera a que termine la operación actual.", emptyFragmentError:"Ningún fragmento puede estar vacío.", savedDrafts:"Texto guardado. Los fragmentos editados quedan pendientes de generar.", saveError:"Error al guardar", errorPrefix:"No se pudo guardar: ", naturalSaveError:"Error al guardar", statusSaved:"Guardado", statusSaving:"Guardando…", statusOffline:"Sin conexión"
  }
};
const state = { voices: [], projects: [], project: null, recordedFile: null, recorder: null, stream: null, timer: null, seconds: 0, busy: false, settingsPromise: Promise.resolve(), language: localStorage.getItem("voz-local-language") === "es" ? "es" : "en" };
Object.assign(translations.en, {
  textToSpeech: "Create audio", textToSpeechTitle: "Turn your text into audio",
  writeScriptChooseVoice: "Choose a voice and write what you want it to say.",
  stepVoice: "Choose a voice", stepVoiceHelp: "Add a recording in My voices first.",
  stepText: "Write your text", stepTextHelp: "Paste the words you want to hear.",
  stepAudio: "Generate and download", stepAudioHelp: "Continue, then press Generate audio.",
  howItWorks: "How it works", prepareProject: "Choose your voice", createProject: "Continue to audio",
  continueHelp: "Your text will be saved. On the next screen, press Generate audio.",
  optionalProjectName: "Project name (optional)", projectNamePlaceholder: "Leave empty to use the first words of your text",
  advancedOptions: "Advanced options", technicalDetails: "Technical details", systemStatus: "System status",
  firstVoiceHelp: "Start by adding a voice. You only need to do this once.",
  voiceInstructions: "Name your voice, write what you will say, then record it or upload the recording.",
  exactSampleText: "What does the recording say?", profileName: "Voice name",
  fullAudioHelp: "One recording for your whole text. Recommended to start.",
  modelChooserHelp: "1.7B prioritizes quality. 0.6B uses less memory. Eco uses the same 0.6B model with timbre only; the voice may sound less like the sample.",
  voiceSettings: "Advanced voice settings", voiceSettingsHelp: "Optional: model and voice adjustments",
  editorPending: "Press Generate audio, then listen and download. Long texts may take several minutes.",
  editorReady: "Listen to your audio. Download MP3 for your videos, or WAV for editing.",
  editorPartial: "Generate the remaining parts to download the complete narration.",
  completeFields: "Choose a voice and write your text.", fullProjectCreated: "Text saved. Press Generate audio to hear it.",
  projectCreated: "Text saved in {count} parts. Press Generate pending to create the audio.",
  noVoiceProfiles: "No voices yet. Record or upload a sample using the form to get started.",
  createProjectToSee: "Choose a voice and write your text in Create audio to get started."
});
Object.assign(translations.es, {
  textToSpeech: "Crear audio", textToSpeechTitle: "Convierte tu texto en audio",
  writeScriptChooseVoice: "Elige una voz y escribe lo que quieres que diga.",
  stepVoice: "Elige una voz", stepVoiceHelp: "Primero añade una grabación en Mis voces.",
  stepText: "Escribe tu texto", stepTextHelp: "Pega las palabras que quieres escuchar.",
  stepAudio: "Genera y descarga", stepAudioHelp: "Continúa y pulsa Generar audio.",
  howItWorks: "Cómo se usa", prepareProject: "Elige tu voz", createProject: "Continuar al audio",
  continueHelp: "Se guardará tu texto. En la siguiente pantalla, pulsa Generar audio.",
  optionalProjectName: "Nombre del proyecto (opcional)", projectNamePlaceholder: "Si lo dejas vacío, se usarán las primeras palabras del texto",
  advancedOptions: "Opciones avanzadas", technicalDetails: "Detalles técnicos", systemStatus: "Estado del sistema",
  firstVoiceHelp: "Empieza añadiendo una voz. Solo necesitas hacerlo una vez.",
  voiceInstructions: "Pon un nombre a tu voz, escribe lo que vas a decir y grábalo o sube la grabación.",
  exactSampleText: "¿Qué dice la grabación?", profileName: "Nombre de la voz",
  fullAudioHelp: "Una grabación con todo tu texto. Recomendado para empezar.",
  modelChooserHelp: "1.7B prioriza la calidad. 0.6B usa menos memoria. Eco usa el mismo modelo 0.6B con solo timbre; puede parecerse menos a la muestra.",
  voiceSettings: "Ajustes avanzados de voz", voiceSettingsHelp: "Opcional: modelo y ajustes de la voz",
  editorPending: "Pulsa Generar audio, escúchalo y descárgalo. Los textos largos pueden tardar varios minutos.",
  editorReady: "Escucha tu audio. Descarga MP3 para tus vídeos o WAV para editarlo.",
  editorPartial: "Genera las partes pendientes para descargar la narración completa.",
  completeFields: "Elige una voz y escribe tu texto.", fullProjectCreated: "Texto guardado. Pulsa Generar audio para escucharlo.",
  projectCreated: "Texto guardado en {count} partes. Pulsa Generar pendientes para crear el audio.",
  noVoiceProfiles: "Aún no tienes voces. Graba o sube una muestra con el formulario para empezar.",
  createProjectToSee: "Elige una voz y escribe tu texto en Crear audio para empezar."
});
const installationCopy = {
  gpuAvailable: ["● GPU available", "● GPU disponible"],
  cpuActive: ["● CPU mode · slower", "● Modo CPU · más lento"],
  installation: ["Installation", "Instalación"],
  installIntro: ["Set up Voz Local on another computer. Choose your operating system.", "Prepara Voz Local en otro equipo. Elige tu sistema operativo."],
  installNeed: ["What do I need?", "¿Qué necesito?"],
  installNeedHelp: ["The web needs a local server, Python, FFmpeg and a downloaded Qwen3-TTS voice model. Ollama is optional and only helps with writing.", "La web necesita un servidor local, Python, FFmpeg y un modelo de voz Qwen3-TTS descargado. Ollama es opcional y solo ayuda a escribir."],
  installAvailability: ["The current installer is specific to Linux with the RX 9060 XT. A universal automatic installer is not available yet.", "El instalador actual es específico para Linux con la RX 9060 XT. Todavía no hay un instalador automático universal."],
  operatingSystem: ["Operating system", "Sistema operativo"],
  installAvailable: ["Installer available", "Instalador disponible"],
  installPreparation: ["Preparation guide", "Guía de preparación"],
  linuxScope: ["For the current Ubuntu + Radeon RX 9060 XT setup. Other GPUs and distributions need a different PyTorch setup.", "Para la configuración actual: Ubuntu y Radeon RX 9060 XT. Otras tarjetas y distribuciones necesitan una instalación de PyTorch diferente."],
  installGetProject: ["Download and extract the project", "Descarga y extrae el proyecto"],
  installFolderHelp: ["Open a terminal in the extracted Voz Local folder. Keep it there: your voices and projects will be saved in its data folder.", "Abre una terminal en la carpeta extraída de Voz Local. Consérvala: las voces y los proyectos se guardarán en su carpeta data."],
  installPrerequisites: ["Prepare the dependencies", "Prepara las dependencias"],
  linuxDeps: ["On Ubuntu, install Python's environment tools and FFmpeg. The command may ask for your computer password.", "En Ubuntu, instala las herramientas de entorno de Python y FFmpeg. El comando puede pedir la contraseña de tu equipo."],
  installRun: ["Run the installer", "Ejecuta el instalador"],
  linuxInstallerDoes: ["It creates a separate Python 3.12 environment, installs the AMD build of PyTorch and the app libraries, and downloads Qwen3-TTS 1.7B. Internet is needed; allow time for the download.", "Crea un entorno separado de Python 3.12, instala PyTorch para AMD y las bibliotecas de la web, y descarga Qwen3-TTS 1.7B. Necesita internet; la descarga puede tardar."],
  installLaunch: ["Start the web", "Inicia la web"],
  installKeepTerminal: ["Keep this terminal open while you use the app. Press Ctrl+C to stop the server.", "Mantén esta terminal abierta mientras usas la web. Pulsa Ctrl+C para apagar el servidor."],
  windowsScope: ["Voz Local does not have a native Windows installer yet. The current Linux script is not a Windows installer.", "Voz Local todavía no tiene un instalador nativo para Windows. El script actual de Linux no es un instalador de Windows."],
  windowsPython: ["Prepare Python 3.12", "Prepara Python 3.12"],
  windowsPythonHelp: ["Use the official Python downloads. If using the traditional installer, enable Add Python to PATH.", "Usa las descargas oficiales de Python. Si utilizas el instalador tradicional, activa Add Python to PATH."],
  pythonOfficial: ["Official Python downloads ↗", "Descargas oficiales de Python ↗"],
  installAudioTools: ["Prepare the audio tools", "Prepara las herramientas de audio"],
  windowsAudioHelp: ["Install FFmpeg and make it available in PATH. The project uses it to read recordings and export MP3.", "Instala FFmpeg y añádelo al PATH. El proyecto lo utiliza para leer grabaciones y exportar MP3."],
  ffmpegOfficial: ["FFmpeg downloads ↗", "Descargas de FFmpeg ↗"],
  installGpuSetup: ["Adapt the voice engine to the computer", "Adapta el motor de voz al equipo"],
  windowsGpuHelp: ["PyTorch must match the GPU and driver. This app currently selects the RX 9060 XT specifically; a Windows launcher and compatible GPU selection still need to be implemented. Installing Python alone will not enable voice generation.", "PyTorch debe ser compatible con la tarjeta y su controlador. Esta app selecciona específicamente la RX 9060 XT; faltan un iniciador para Windows y una selección de GPU compatible. Instalar Python por sí solo no habilita la generación de voz."],
  pytorchOfficial: ["Official PyTorch installation guide ↗", "Guía oficial de instalación de PyTorch ↗"],
  macScope: ["Voz Local does not have a macOS installer yet. The current installer uses AMD ROCm and cannot be used on a Mac.", "Voz Local todavía no tiene un instalador para macOS. El instalador actual usa AMD ROCm y no se puede utilizar en un Mac."],
  macPython: ["Prepare Python 3.12", "Prepara Python 3.12"],
  macPythonHelp: ["Download Python from its official site. The project also needs FFmpeg for recordings and MP3 export.", "Descarga Python desde su página oficial. El proyecto también necesita FFmpeg para las grabaciones y la exportación MP3."],
  macGpuHelp: ["PyTorch offers an MPS backend for supported Macs, but this project has not integrated or verified Qwen3-TTS with it. A Mac launcher and an adapted engine are still needed before generating audio.", "PyTorch ofrece el motor MPS para Macs compatibles, pero este proyecto todavía no ha integrado ni comprobado Qwen3-TTS con él. Faltan un iniciador para Mac y la adaptación del motor antes de generar audio."],
  mpsOfficial: ["Official PyTorch MPS documentation ↗", "Documentación oficial de PyTorch MPS ↗"],
  installQuestions: ["Common questions", "Preguntas frecuentes"],
  installOllamaQuestion: ["Do I need Ollama?", "¿Necesito Ollama?"],
  installOllamaAnswer: ["No. Qwen3-TTS generates the voice directly. Install Ollama only if you want help editing scripts.", "No. Qwen3-TTS genera la voz directamente. Instala Ollama solo si quieres ayuda para editar guiones."],
  ollamaOfficial: ["Optional: download Ollama ↗", "Opcional: descargar Ollama ↗"],
  installInternetQuestion: ["Do I need internet every time?", "¿Necesito internet siempre?"],
  installInternetAnswer: ["Internet is needed to install dependencies and download each model the first time. Once downloaded, voice generation is local. Selecting a model you do not have may trigger a download.", "Necesitas internet para instalar dependencias y descargar cada modelo la primera vez. Después, la generación de voz es local. Elegir un modelo que no tienes puede iniciar una descarga."],
  installBrowserQuestion: ["Why does the web not open?", "¿Por qué no se abre la web?"],
  installBrowserAnswer: ["The server must be running on the same computer as the browser. A localhost link alone does not install or start Voz Local. On this Ubuntu setup, run bash iniciar.sh again after restarting the computer.", "El servidor debe estar encendido en el mismo equipo que el navegador. Un enlace localhost no instala ni inicia Voz Local por sí solo. En esta configuración de Ubuntu, ejecuta bash iniciar.sh después de reiniciar el equipo."],
  installAutomaticQuestion: ["Will everything install automatically?", "¿Se instala todo automáticamente?"],
  installAutomaticAnswer: ["The current Linux script installs the project environment and the 1.7B voice model. It requires FFmpeg and Python environment tools beforehand, and does not install system GPU drivers. Automatic Windows and macOS installers still need to be built.", "El script actual de Linux instala el entorno del proyecto y el modelo de voz 1.7B. Requiere FFmpeg y las herramientas de entorno de Python previamente, y no instala los controladores de la GPU. Todavía hay que crear los instaladores automáticos para Windows y macOS."],
  installSources: ["Voice model documentation:", "Documentación del modelo de voz:"]
};
for (const [key, [en, es]] of Object.entries(installationCopy)) {
  translations.en[key] = en;
  translations.es[key] = es;
}
const automaticInstallCopy = {
  downloadInstaller: ["Download project ZIP", "Descargar proyecto ZIP"],
  installerPackageHelp: ["Includes the app and launchers. Python and the voice model download on the destination computer. Your voices and projects are not included.", "Incluye la app y los iniciadores. Python y el modelo se descargan en el equipo de destino. No incluye tus voces ni tus proyectos."],
  installAvailability: ["Automatic launchers are included. Windows and macOS have not been tested on real machines yet. GPU drivers must already be installed; unsupported GPUs use the slower CPU mode.", "Se incluyen iniciadores automáticos. Windows y macOS todavía no se han probado en equipos reales. Los controladores de GPU deben estar instalados; las tarjetas no compatibles usan el modo CPU, más lento."],
  linuxScope: ["The launcher prepares dependencies on Ubuntu/Debian, Fedora or Arch. It selects CUDA for NVIDIA with a driver, the existing ROCm setup for RX 9060 XT, or CPU for other computers.", "El iniciador prepara dependencias en Ubuntu/Debian, Fedora o Arch. Selecciona CUDA para NVIDIA con controlador, la configuración ROCm existente para RX 9060 XT o CPU para otros equipos."],
  linuxInstallerDoes: ["Installs FFmpeg if missing, prepares an isolated Python 3.12 environment and app libraries, downloads Qwen3-TTS 1.7B, and starts the web. It needs internet the first time and may ask for your system password.", "Instala FFmpeg si falta, prepara un entorno aislado de Python 3.12 y las bibliotecas, descarga Qwen3-TTS 1.7B e inicia la web. La primera vez necesita internet y puede pedir la contraseña del sistema."],
  windowsScope: ["Launcher included for Windows. NVIDIA uses CUDA when a driver is present; AMD and other computers default to CPU. This installation has not been tested on a real Windows PC yet.", "Se incluye un iniciador para Windows. NVIDIA usa CUDA si hay controlador; AMD y otros equipos usan CPU por defecto. Esta instalación todavía no se ha probado en un PC Windows real."],
  macScope: ["Launcher included for Apple Silicon Macs (M1 or later). It uses CPU by default, which can be slow. MPS acceleration is experimental and opt-in. This installation has not been tested on a real Mac yet. Intel Macs are not supported by this installer.", "Se incluye un iniciador para Mac Apple Silicon (M1 o posterior). Usa CPU por defecto y puede ser lento. La aceleración MPS es experimental y opcional. Esta instalación todavía no se ha probado en un Mac real. El instalador no admite Macs Intel."],
  extractAll: ["Extract the whole project, including the scripts folder. The launcher cannot run by itself. Do not copy the .venv environment from another computer.", "Extrae el proyecto completo, incluida la carpeta scripts. El iniciador no funciona por sí solo. No copies el entorno .venv de otro equipo."],
  windowsRun: ["Double-click the launcher", "Haz doble clic en el iniciador"],
  windowsAutomatic: ["It downloads a private Python 3.12 runtime if missing, installs FFmpeg using WinGet, prepares the dependencies and downloads the voice model. Windows may ask for installation permissions.", "Descarga un Python 3.12 propio si falta, instala FFmpeg mediante WinGet, prepara las dependencias y descarga el modelo de voz. Windows puede pedir permisos de instalación."],
  windowsWinget: ["If WinGet is unavailable, install Microsoft's App Installer and run the .bat again. If FFmpeg was just installed, you may need to reopen the .bat to refresh PATH.", "Si no tienes WinGet, instala App Installer de Microsoft y ejecuta el .bat otra vez. Si FFmpeg acaba de instalarse, puede ser necesario reabrir el .bat para actualizar el PATH."],
  repeatLauncher: ["Use the same launcher next time. Completed dependencies and downloads are reused.", "Usa el mismo iniciador la próxima vez. Reutiliza las dependencias y descargas ya completadas."],
  macRun: ["Open the Mac launcher", "Abre el iniciador para Mac"],
  macAutomatic: ["It prepares Python 3.12 and installs FFmpeg with Homebrew, installing Homebrew from its official source if missing. It then prepares the dependencies and voice model. If the .command does not open, run the following in a terminal inside the project folder:", "Prepara Python 3.12 e instala FFmpeg con Homebrew, instalando Homebrew desde su fuente oficial si falta. Después prepara las dependencias y el modelo. Si el .command no se abre, ejecuta lo siguiente en una terminal dentro de la carpeta del proyecto:"],
  installAutomaticAnswer: ["The launchers prepare Python, app libraries and the voice model; they install FFmpeg using the system package manager when available. Permissions or license prompts may appear. They do not install GPU drivers. JavaScript, HTML and CSS run in your browser: no Node.js or Java installation is needed.", "Los iniciadores preparan Python, las bibliotecas y el modelo de voz; instalan FFmpeg con el gestor del sistema cuando está disponible. Pueden aparecer permisos o licencias. No instalan controladores de GPU. JavaScript, HTML y CSS funcionan en el navegador: no necesitas instalar Node.js ni Java."],
  installBrowserAnswer: ["The server must be running on the same computer as the browser. Run your platform's Install and start launcher again after restarting the computer. Keep its window open during use.", "El servidor debe estar encendido en el mismo equipo que el navegador. Después de reiniciar, abre de nuevo el iniciador Instalar e iniciar de tu sistema. Mantén su ventana abierta mientras usas la web."]
};
for (const [key, [en, es]] of Object.entries(automaticInstallCopy)) {
  translations.en[key] = en;
  translations.es[key] = es;
}
function t(key, vars = {}) { const value = translations[state.language]?.[key] ?? translations.en[key] ?? key; return value.replace(/\{(\w+)\}/g, (_, name) => vars[name] ?? ""); }
function applyLanguage() {
  document.documentElement.lang = state.language;
  const select = $("language-select"); if (select) select.value = state.language;
  document.querySelector(".brand")?.setAttribute("aria-label", state.language === "en" ? "Voz Local, go to Text to speech" : "Voz Local, ir a Texto a voz");
  document.querySelector(".side-nav")?.setAttribute("aria-label", state.language === "en" ? "Sections" : "Secciones");
  select?.setAttribute("aria-label", t("language"));
  if (select) select.setAttribute("aria-label", t("language"));
  document.querySelector(".side-nav")?.setAttribute("aria-label", state.language === "en" ? "Sections" : "Secciones");
  document.querySelector(".brand")?.setAttribute("aria-label", state.language === "en" ? "Voz Local, go to Text to speech" : "Voz Local, ir a Texto a voz");
  document.querySelectorAll("[data-i18n]").forEach(el => { el.textContent = t(el.dataset.i18n); });
  document.querySelectorAll("[data-i18n-placeholder]").forEach(el => { el.placeholder = t(el.dataset.i18nPlaceholder); });
  $("quick-steps").setAttribute("aria-label", t("howItWorks"));
  $("install-tabs").setAttribute("aria-label", t("operatingSystem"));
  showView(); updateCount(); updateSettingLabels();
  if (state.project) renderProject();
}
const views = ["guion", "voces", "proyecto", "instalacion"];

function showView() {
  const current = location.hash.slice(1);
  const view = views.includes(current) ? current : "guion";
  document.title = `Voz Local · ${{ guion: t("textToSpeech"), voces: t("myVoices"), proyecto: t("projects"), instalacion: t("installation") }[view]}`;
  for (const name of views) $(name).hidden = name !== view;
  document.querySelectorAll(".side-nav a[data-view]").forEach(link => {
    const active = link.dataset.view === view;
    link.classList.toggle("active", active);
    if (active) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  });
  window.scrollTo(0, 0);
}

function goToView(view) {
  if (location.hash !== `#${view}`) location.hash = view;
  else showView();
}

function selectInstallationOS(os, focus = false) {
  document.querySelectorAll("[data-install-os]").forEach(button => {
    const selected = button.dataset.installOs === os;
    button.setAttribute("aria-selected", String(selected));
    button.tabIndex = selected ? 0 : -1;
    $(`install-${button.dataset.installOs}`).hidden = !selected;
    if (selected && focus) button.focus();
  });
}
document.querySelectorAll("[data-install-os]").forEach(button => {
  button.addEventListener("click", () => selectInstallationOS(button.dataset.installOs));
  button.addEventListener("keydown", event => {
    const systems = ["linux", "windows", "mac"];
    const current = systems.indexOf(button.dataset.installOs);
    let next;
    if (event.key === "ArrowRight") next = (current + 1) % systems.length;
    else if (event.key === "ArrowLeft") next = (current + systems.length - 1) % systems.length;
    else if (event.key === "Home") next = 0;
    else if (event.key === "End") next = systems.length - 1;
    else return;
    event.preventDefault();
    selectInstallationOS(systems[next], true);
  });
});

function message(text, error = false) {
  const notice = $("notice");
  notice.textContent = text;
  notice.classList.toggle("error", error);
  notice.hidden = false;
  notice.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

async function api(path, options = {}) {
  const response = await fetch(path, options);
  if (!response.ok) {
    let detail = `Error ${response.status}`;
    try { detail = (await response.json()).detail || detail; } catch (_) {}
    throw new Error(Array.isArray(detail) ? detail.map(x => x.msg).join("; ") : detail);
  }
  return response.json();
}

function make(tag, className, content) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (content !== undefined) node.textContent = content;
  return node;
}

async function loadStatus() {
  try {
    const status = await api("/api/status");
    const gpu = $("gpu-status");
    gpu.textContent = status.gpu_available ? `${t("gpuAvailable")} · ${status.runtime?.backend || ""}` : status.runtime?.device === "cpu" ? t("cpuActive") : t("gpuUnavailable");
    gpu.classList.toggle("bad", !status.gpu_available && status.runtime?.device !== "cpu");
    const installed = status.voice_model?.installed ?? status.model_downloaded;
    const activeSize = status.voice_model?.active_size;
    const modelName = activeSize === "0.6B" ? "Qwen3-TTS 0.6B Base" : "Qwen3-TTS 1.7B Base";
    $("voice-model-name").textContent = modelName;
    $("voice-model-description").textContent = activeSize === "0.6B"
      ? t("modelFallback")
      : t("modelDescription");
    $("voice-model-state").textContent = activeSize ? t("modelInUse") : installed ? t("modelInstalled") : t("modelMissing");
    $("voice-model-state").classList.toggle("unavailable", !installed && !activeSize);
    $("model-status").textContent = `${modelName} · ${activeSize ? t("modelInUse") : installed ? t("modelInstalled") : t("modelMissing")}`;
    $("model-status").classList.toggle("muted", !installed && !activeSize);
  } catch (error) {
    $("gpu-status").textContent = t("offline");
    $("gpu-status").classList.add("bad");
    $("voice-model-state").textContent = t("statusOffline");
    $("voice-model-description").textContent = t("noConnection");
  }
}

async function loadVoices() {
  state.voices = await api("/api/voices");
  const list = $("voice-list");
  list.replaceChildren();
  const select = $("project-voice");
  const previous = select.value;
  select.replaceChildren(new Option(t("selectVoice"), ""));
  if (!state.voices.length) list.append(make("p", "empty", t("noVoiceProfiles")));
  state.voices.forEach(voice => {
    select.add(new Option(voice.name, voice.id));
    const card = make("div", "voice-card");
    const top = make("div", "voice-card-top");
    top.append(make("span", "voice-avatar", "◉"));
    const details = make("div");
    details.append(make("strong", "", voice.name), make("small", "", `${voice.duration.toFixed(1)} ${t("secondsSample")}`));
    const remove = make("button", "voice-delete", t("delete"));
    remove.type = "button";
    remove.setAttribute("aria-label", t("deleteVoice", { name: voice.name }));
    remove.addEventListener("click", () => deleteVoice(voice));
    top.append(details, remove);
    card.append(top);
    const player = make("audio");
    player.controls = true;
    player.preload = "none";
    player.src = `/api/voices/${voice.id}/audio`;
    card.append(player);
    const warning = make("p", "voice-warning");
    const updateWarning = () => {
      const words = voice.transcript.match(/\p{L}+/gu)?.length || 0;
      warning.hidden = !words || voice.duration / words <= 0.85;
      warning.textContent = t("sampleWarning", { duration: voice.duration.toFixed(1), words });
    };
    updateWarning();
    card.append(warning);
    if (voice.duration > 8) {
      card.append(make("p", "voice-length-tip", t("longSampleTip")));
    }
    const editor = make("details", "transcript-editor");
    if (!warning.hidden) editor.open = true;
    const summary = make("summary", "", t("editSampleText"));
    const transcriptLabel = make("label", "", t("exactWordsHeard"));
    const transcriptInput = make("textarea");
    transcriptInput.id = `transcript-${voice.id}`;
    transcriptInput.rows = 4;
    transcriptInput.maxLength = 2000;
    transcriptInput.value = voice.transcript;
    transcriptLabel.htmlFor = transcriptInput.id;
    const saveTranscript = make("button", "button secondary", t("saveTranscript"));
    saveTranscript.type = "button";
    const transcriptStatus = make("small", "transcript-status", t("transcriptHelp"));
    saveTranscript.addEventListener("click", async () => {
      if (state.busy) { transcriptStatus.textContent = t("waitOperation"); return; }
      const transcript = transcriptInput.value.trim();
      if (!transcript) { transcriptStatus.textContent = t("transcriptRequired"); return; }
      state.busy = true;
      saveTranscript.disabled = true;
      remove.disabled = true;
      transcriptStatus.textContent = t("saving");
      try {
        const updated = await api(`/api/voices/${voice.id}/transcript`, {
          method: "PATCH", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ transcript })
        });
        Object.assign(voice, updated);
        updateWarning();
        transcriptStatus.textContent = t("transcriptSaved");
      } catch (error) {
        transcriptStatus.textContent = t("transcriptSaveError", { error: error.message });
      } finally {
        state.busy = false;
        saveTranscript.disabled = false;
        remove.disabled = false;
      }
    });
    editor.append(summary, transcriptLabel, transcriptInput, saveTranscript, transcriptStatus);
    card.append(editor);
    list.append(card);
  });
  if (state.voices.some(voice => voice.id === previous)) select.value = previous;
  else if (state.voices.length) select.value = state.voices[0].id;
  $("first-voice-help").hidden = state.voices.length > 0;
  $("project-form").querySelector('button[type="submit"]').disabled = !state.voices.length;
}

async function deleteVoice(voice) {
  if (state.busy) { message(t("waitOperation"), true); return; }
  try {
    await loadProjects();
    const linked = state.projects.filter(project => project.voice_id === voice.id);
    const names = linked.slice(0, 5).map(project => `• ${project.title}`).join("\n");
    const projectsWarning = linked.length
      ? `\n\n${t("projectsAlsoDeleted", { count: linked.length })}\n${names}${linked.length > 5 ? "\n• …" : ""}`
      : "";
    if (!window.confirm(`${t("deleteVoiceConfirm", { name: voice.name })}${projectsWarning}\n\n${t("cannotUndo")}`)) return;
    state.busy = true;
    await api(`/api/voices/${voice.id}`, {
      method: "DELETE", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_ids: linked.map(project => project.id) })
    });
    if (linked.some(project => project.id === state.project?.id)) {
      state.project = null;
      renderProject();
    }
    await loadVoices();
    await loadProjects();
    if (!state.project && state.projects.length) await openProject(state.projects[0].id);
    message(t("voiceDeleted", { name: voice.name, extra: linked.length ? t("withProjects", { count: linked.length }) : "" }));
  } catch (error) { message(error.message, true); }
  finally { state.busy = false; }
}

async function loadProjects() {
  state.projects = await api("/api/projects");
  const list = $("project-list");
  list.replaceChildren();
  if (!state.projects.length) {
    list.append(make("p", "empty", t("noProjects")));
    return;
  }
  state.projects.forEach(project => {
    const row = make("div", "project-row");
    const item = make("button", "project-item");
    item.type = "button";
    if (state.project?.id === project.id) item.classList.add("active");
    const projectMode = project.mode === "continuous" ? t("fullAudio") : `${project.chunk_count} ${project.chunk_count === 1 ? t("fragment") : t("fragmentsWord")}`;
    item.append(make("strong", "", project.title), make("small", "", `${projectMode} · ${project.voice_name}`));
    item.addEventListener("click", () => openProject(project.id));
    const remove = make("button", "project-delete", t("delete"));
    remove.type = "button";
    remove.setAttribute("aria-label", t("deleteProject", { name: project.title }));
    remove.addEventListener("click", () => deleteProject(project));
    row.append(item, remove);
    list.append(row);
  });
}

async function deleteProject(project) {
  if (state.busy) { message(t("waitOperation"), true); return; }
  if (!window.confirm(t("deleteProjectConfirm", { name: project.title }))) return;
  state.busy = true;
  try {
    await api(`/api/projects/${project.id}`, { method: "DELETE" });
    if (state.project?.id === project.id) {
      state.project = null;
      renderProject();
    }
    await loadProjects();
    if (!state.project && state.projects.length) await openProject(state.projects[0].id);
    message(t("projectDeleted", { name: project.title }));
  } catch (error) { message(error.message, true); }
  finally { state.busy = false; }
}

async function openProject(id) {
  try {
    await state.settingsPromise;
    if (state.project && state.project.id !== id && !state.busy) await saveDrafts();
    state.project = await api(`/api/projects/${id}`);
    renderProject();
    await loadProjects();
  } catch (error) { message(error.message, true); }
}

function renderProject() {
  const project = state.project;
  $("project-empty").hidden = Boolean(project);
  $("project-editor").hidden = !project;
  if (!project) return;
  renderVoiceSettings(project.settings);
  $("project-mode-switch").value = project.mode;
  $("apply-project-mode").disabled = true;
  $("selected-project-title").textContent = project.title;
  const continuous = project.mode === "continuous";
  const generated = project.chunks.filter(x => x.audio_url).length;
  const canExport = project.chunks.length > 0 && generated === project.chunks.length;
  $("export-wav").disabled = !canExport;
  $("export-mp3").disabled = !canExport;
  $("editor-guide").textContent = t(canExport ? "editorReady" : generated ? "editorPartial" : "editorPending");
  $("selected-project-meta").textContent = continuous
    ? `${project.voice_name} · ${t("fullAudio")} · ${generated ? t("generated") : t("pending")}`
    : `${project.voice_name} · ${project.chunks.length} ${project.chunks.length === 1 ? t("fragment") : t("fragmentsWord")} · ${generated} ${t("generated").toLowerCase()}`;
  $("generate-all").textContent = continuous
    ? generated ? t("regenerateAudio") : t("generateAudio")
    : t("generatePending");
  const list = $("chunk-list");
  list.replaceChildren();
  project.chunks.forEach((chunk, index) => {
    const card = make("article", "chunk-card");
    if (continuous) card.classList.add("continuous");
    card.dataset.chunkId = chunk.id;
    const top = make("div", "chunk-top");
    top.append(make("span", "chunk-number", continuous ? t("narrationFull") : t("fragmentLabel", { n: String(index + 1).padStart(2, "0") })));
    top.append(make("span", "chunk-state", chunk.audio_url ? t("generatedModel", { model: chunk.model_size }) : t("pending")));
    const textarea = make("textarea");
    textarea.value = chunk.text;
    textarea.maxLength = continuous ? 30000 : 350;
    textarea.rows = continuous ? 10 : 3;
    textarea.setAttribute("aria-label", continuous ? t("narrationText") : t("fragmentText", { n: index + 1 }));
    const actions = make("div", "chunk-actions");
    if (chunk.audio_url) {
      const player = make("audio");
      player.controls = true;
      player.preload = "none";
      player.src = chunk.audio_url;
      const variant = make("div", "audio-variant");
      variant.append(make("span", "", chunk.raw_audio_url ? t("qwenOriginal") : t("oldAudio")), player);
      actions.append(variant);
    } else actions.append(make("span", "empty", t("audioPending")));
    const save = make("button", "button secondary", t("saveText"));
    save.type = "button";
    save.addEventListener("click", saveText);
    const button = make("button", "button secondary", continuous
      ? chunk.audio_url ? t("regenerateAudio") : t("generateAudio")
      : chunk.audio_url ? t("regenerate") : t("generate"));
    button.type = "button";
    button.addEventListener("click", () => generateOne(chunk.id));
    actions.append(save);
    if (!continuous) actions.append(button);
    card.append(top, textarea, actions);
    list.append(card);
  });
}

function settingsFromControls() {
  return {
    model: $("setting-model").value,
    speed: 1,
    speed_method: "rubberband",
    stability: Number($("setting-stability").value),
    similarity: $("setting-similarity").value === "1" ? "reference" : "timbre",
    style: Number($("setting-style").value),
    language_override: $("setting-language-override").checked,
    language: $("setting-language").value,
    audio_effects: false
  };
}

function updateSettingLabels() {
  $("setting-stability-value").textContent = `${$("setting-stability").value} %`;
  const eco = $("setting-model").value === "qwen-0.6b-eco";
  $("setting-similarity-value").textContent = eco ? `${t("timbreOnly")} · Eco` : $("setting-similarity").value === "1" ? t("audioAndText") : t("timbreOnly");
  $("setting-similarity").disabled = eco || state.busy;
  $("setting-style-value").textContent = `${$("setting-style").value} %`;
  $("setting-language-row").hidden = !$("setting-language-override").checked;
}

function renderVoiceSettings(settings) {
  $("setting-model").value = settings.model || "qwen-1.7b";
  $("setting-stability").value = settings.stability;
  $("setting-similarity").value = settings.similarity === "reference" ? "1" : "0";
  $("setting-style").value = settings.style;
  $("setting-language-override").checked = settings.language_override;
  $("setting-language").value = settings.language;
  $("settings-status").textContent = "";
  updateSettingLabels();
}

function saveVoiceSettings() {
  if (!state.project) return Promise.resolve();
  const projectId = state.project.id;
  const settings = settingsFromControls();
  $("settings-status").textContent = t("statusSaving");
  state.settingsPromise = state.settingsPromise.catch(() => {}).then(async () => {
    const saved = await api(`/api/projects/${projectId}/settings`, {
      method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(settings)
    });
    if (state.project?.id === projectId) {
      state.project.settings = saved;
      $("settings-status").textContent = t("statusSaved");
    }
  });
  return state.settingsPromise;
}

function lockVoiceSettings(locked) {
  $("voice-settings").querySelectorAll("input[id^='setting-'], select[id^='setting-']").forEach(control => { control.disabled = locked; });
  $("natural-preset").disabled = locked;
  if (!locked) updateSettingLabels();
}

async function useNaturalPreset() {
  if (!state.project || state.busy) return;
  $("setting-stability").value = "50";
  $("setting-similarity").value = "1";
  $("setting-style").value = "0";
  $("setting-language-override").checked = false;
  $("setting-language").value = "Spanish";
  updateSettingLabels();
  try { await saveVoiceSettings(); }
  catch (error) { $("settings-status").textContent = t("naturalSaveError"); message(error.message, true); }
}

async function saveText() {
  if (state.busy || !state.project) return;
  state.busy = true;
  try {
    await saveDrafts();
    await openProject(state.project.id);
    message(t("savedDrafts"));
  } catch (error) { message(error.message, true); }
  finally { state.busy = false; }
}

async function saveDrafts() {
  if (!state.project) return;
  const id = state.project.id;
  const cards = Array.from($("chunk-list").children);
  for (const card of cards) {
    const chunk = state.project.chunks.find(item => item.id === card.dataset.chunkId);
    const text = card.querySelector("textarea").value.trim();
    if (!text) throw new Error(t("emptyFragmentError"));
    if (text !== chunk.text) {
      const updated = await api(`/api/projects/${id}/chunks/${chunk.id}`, {
        method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text })
      });
      Object.assign(chunk, updated);
    }
  }
}

async function generateOne(chunkId) {
  if (state.busy || !state.project) return;
  state.busy = true;
  lockVoiceSettings(true);
  const continuous = state.project.mode === "continuous";
  $("generation-progress").textContent = continuous
    ? t("generatingFull")
    : t("savingGenerating");
  try {
    await state.settingsPromise;
    await saveDrafts();
    await api(`/api/projects/${state.project.id}/chunks/${chunkId}/generate`, { method: "POST" });
    await openProject(state.project.id);
    await loadStatus();
    message(continuous ? t("fullNarrationGenerated") : t("fragmentGenerated"));
  } catch (error) { message(error.message, true); }
  finally { state.busy = false; lockVoiceSettings(false); $("generation-progress").textContent = ""; }
}

async function generateAll() {
  if (state.busy || !state.project) return;
  if (state.project.mode === "continuous") {
    await generateOne(state.project.chunks[0].id);
    return;
  }
  state.busy = true;
  lockVoiceSettings(true);
  const id = state.project.id;
  try {
    await state.settingsPromise;
    await saveDrafts();
    const pending = state.project.chunks.filter(chunk => !chunk.audio_url);
    if (!pending.length) { message(t("allHaveAudio")); return; }
    for (let index = 0; index < pending.length; index++) {
      $("generation-progress").textContent = `${t("generatePending")} ${index + 1} / ${pending.length}…`;
      await api(`/api/projects/${id}/chunks/${pending[index].id}/generate`, { method: "POST" });
      state.project = await api(`/api/projects/${id}`);
      renderProject();
      await loadStatus();
    }
    await loadProjects();
    message(t("narrationComplete"));
  } catch (error) { message(error.message, true); }
  finally { state.busy = false; lockVoiceSettings(false); $("generation-progress").textContent = ""; }
}

async function applyProjectMode() {
  if (state.busy || !state.project) return;
  const mode = $("project-mode-switch").value;
  if (mode === state.project.mode) return;
  state.busy = true;
  try {
    await state.settingsPromise;
    await saveDrafts();
    const result = await api(`/api/projects/${state.project.id}/mode`, {
      method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ mode })
    });
    state.project = result.project;
    renderProject();
    await loadProjects();
    message(result.copied ? t("copiedMode") : t("modeUpdated"));
  } catch (error) {
    $("project-mode-switch").value = state.project.mode;
    $("apply-project-mode").disabled = true;
    message(error.message, true);
  } finally { state.busy = false; }
}

async function exportAudio(format) {
  if (!state.project || state.busy) return;
  state.busy = true;
  try {
    const response = await fetch(`/api/projects/${state.project.id}/export?format=${format}`, { method: "POST" });
    if (!response.ok) {
      let detail = t("exportError");
      try { detail = (await response.json()).detail || detail; } catch (_) {}
      throw new Error(detail);
    }
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    const title = state.project.title.replace(/[^\p{L}\p{N} _-]/gu, "").trim() || "Voz Local";
    link.download = `${title} - original de Qwen.${format}`;
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 60000);
  } catch (error) { message(error.message, true); }
  finally { state.busy = false; }
}

async function loadOllamaModels() {
  const select = $("ollama-model");
  try {
    const { models } = await api("/api/ollama/models");
    select.replaceChildren();
    if (!models.length) {
      select.add(new Option(t("ollamaUnavailable"), ""));
      $("rewrite-button").disabled = true;
    } else {
      models.forEach(name => select.add(new Option(name, name)));
      $("rewrite-button").disabled = false;
    }
  } catch (_) {
    select.replaceChildren(new Option(t("ollamaUnavailable"), ""));
    $("rewrite-button").disabled = true;
  }
}

async function rewrite() {
  const text = $("script-text").value.trim();
  const model = $("ollama-model").value;
  if (!text || !model) { message(t("writeScriptChooseModel"), true); return; }
  const button = $("rewrite-button");
  button.disabled = true;
  button.textContent = t("editing");
  try {
    const result = await api("/api/ollama/rewrite", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, model, instruction: $("ollama-action").value })
    });
    $("script-text").value = result.text;
    updateCount();
    message(t("scriptEdited"));
  } catch (error) { message(error.message, true); }
  finally { button.disabled = false; button.textContent = `✦ ${t("editText")}`; }
}

function updateCount() { $("char-count").textContent = `${$("script-text").value.length} ${state.language === "en" ? "characters" : "caracteres"}`; }

async function startRecording() {
  if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
    message(t("browserNoRecord"), true); return;
  }
  try {
    state.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mime = ["audio/webm;codecs=opus", "audio/webm", "audio/ogg;codecs=opus"].find(MediaRecorder.isTypeSupported);
    const pieces = [];
    state.recorder = new MediaRecorder(state.stream, mime ? { mimeType: mime } : undefined);
    state.recorder.ondataavailable = event => { if (event.data.size) pieces.push(event.data); };
    state.recorder.onstop = () => {
      const blob = new Blob(pieces, { type: state.recorder.mimeType || "audio/webm" });
      state.recordedFile = new File([blob], "mi-voz.webm", { type: blob.type });
      const preview = $("record-preview");
      if (preview.dataset.url) URL.revokeObjectURL(preview.dataset.url);
      preview.dataset.url = URL.createObjectURL(blob);
      preview.src = preview.dataset.url;
      preview.hidden = false;
      state.stream.getTracks().forEach(track => track.stop());
      $("record-button").hidden = false;
      $("stop-button").hidden = true;
      clearInterval(state.timer);
      $("record-timer").textContent = t("sampleRecorded", { seconds: state.seconds });
    };
    state.seconds = 0;
    $("record-timer").textContent = t("recording", { seconds: 0 });
    state.timer = setInterval(() => { state.seconds++; $("record-timer").textContent = t("recording", { seconds: state.seconds }); }, 1000);
    state.recorder.start();
    $("record-button").hidden = true;
    $("stop-button").hidden = false;
  } catch (error) { message(t("micError"), true); }
}

async function saveVoice(event) {
  event.preventDefault();
  const file = state.recordedFile || $("voice-file").files[0];
  if (!file) { message(t("recordOrSelect"), true); return; }
  const button = $("save-voice-button");
  button.disabled = true;
  try {
    const body = new FormData();
    body.append("name", $("voice-name").value);
    body.append("transcript", $("voice-transcript").value);
    body.append("file", file);
    const voice = await api("/api/voices", { method: "POST", body });
    state.recordedFile = null;
    $("voice-file").value = "";
    $("record-preview").hidden = true;
    $("record-timer").textContent = "";
    await loadVoices();
    $("project-voice").value = voice.id;
    goToView("guion");
    message(t("voiceSaved"));
  } catch (error) { message(error.message, true); }
  finally { button.disabled = false; }
}

async function createProject(event) {
  event.preventDefault();
  const voice_id = $("project-voice").value;
  const script = $("script-text").value.trim();
  const title = $("project-title").value.trim() || script.replace(/\s+/g, " ").slice(0, 80);
  const mode = $("project-form").elements["project-mode"].value;
  const voice_model = $("project-voice-model").value;
  if (!title || !voice_id || !script) { message(t("completeFields"), true); return; }
  const button = $("project-form").querySelector('button[type="submit"]');
  button.disabled = true;
  try {
    const project = await api("/api/projects", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, voice_id, script, mode, voice_model })
    });
    await openProject(project.id);
    goToView("proyecto");
    message(mode === "continuous" ? t("fullProjectCreated") : t("projectCreated", { count: project.chunks.length }));
  } catch (error) { message(error.message, true); }
  finally { button.disabled = false; }
}

$("voice-form").addEventListener("submit", saveVoice);
window.addEventListener("hashchange", showView);
$("project-form").addEventListener("submit", createProject);
$("record-button").addEventListener("click", startRecording);
$("stop-button").addEventListener("click", () => state.recorder?.stop());
$("voice-file").addEventListener("change", () => { state.recordedFile = null; });
$("script-text").addEventListener("input", updateCount);
$("rewrite-button").addEventListener("click", rewrite);
$("generate-all").addEventListener("click", generateAll);
$("apply-project-mode").addEventListener("click", applyProjectMode);
$("project-mode-switch").addEventListener("change", () => {
  $("apply-project-mode").disabled = !state.project || $("project-mode-switch").value === state.project.mode;
});
$("export-wav").addEventListener("click", () => exportAudio("wav"));
$("export-mp3").addEventListener("click", () => exportAudio("mp3"));
$("natural-preset").addEventListener("click", useNaturalPreset);
$("voice-settings").querySelectorAll("input[id^='setting-'], select[id^='setting-']").forEach(control => {
  control.addEventListener("input", updateSettingLabels);
  control.addEventListener("change", () => { saveVoiceSettings().catch(error => {
    $("settings-status").textContent = t("saveError");
    message(error.message, true);
  }); });
});

async function boot() {
  applyLanguage();
  try {
    await Promise.all([loadStatus(), loadVoices(), loadProjects(), loadOllamaModels()]);
    if (state.projects.length) await openProject(state.projects[0].id);
  } catch (error) { message(t("startupError", { error: error.message }), true); }
}
$ ("language-select").addEventListener("change", () => {
  state.language = $("language-select").value === "es" ? "es" : "en";
  localStorage.setItem("voz-local-language", state.language);
  applyLanguage();
  loadVoices().catch(() => {});
  loadProjects().catch(() => {});
  loadStatus().catch(() => {});
  loadOllamaModels().catch(() => {});
});
boot();
