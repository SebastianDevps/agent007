# Cómo Publicar Agent007 como Plugin de Claude Code

Guía simple para publicar Agent007 en GitHub y hacerlo disponible como plugin.

---

## 📦 Estructura Actual (Lista para Publicar)

```
Agent007/
├── .claude-plugin/
│   └── plugin.json          ✅ Manifest del plugin
├── .gitignore               ✅ Ignora .claude/ legacy
├── agents/                  ✅ 5 expertos
├── skills/                  ✅ 17 skills
├── commands/                ✅ Comandos custom
├── settings.json            ✅ Configuración por defecto
├── VERSION                  ✅ 2.0.0
├── LICENSE                  ✅ MIT
├── README.md                ✅ Documentación principal
├── INSTALLATION.md          ✅ Guía de instalación
└── PLUGIN.md                ✅ Guía técnica
```

---

## 🚀 Paso a Paso: Publicar en GitHub

### 1. Inicializar Git

```bash
cd /Users/sebasing/Projects/Agent007

# Inicializar repositorio
git init

# Agregar todos los archivos
git add .

# Primer commit
git commit -m "Agent007 v2.0.0 - Claude Code plugin"
```

### 2. Crear Repositorio en GitHub

1. Ve a: **https://github.com/new**

2. Configuración del repositorio:
   - **Nombre**: `agent007`
   - **Descripción**: `Agent007 - Intelligent Development Orchestration System`
   - **Visibilidad**: ✅ **Public** (importante para que otros lo instalen)
   - **NO** inicialices con README (ya tienes uno)

3. Click: **"Create repository"**

### 3. Conectar y Subir

Copia los comandos que GitHub te muestra (o usa estos):

```bash
# Conectar con GitHub (reemplaza TU-USUARIO)
git remote add origin https://github.com/TU-USUARIO/agent007.git

# Renombrar branch a main
git branch -M main

# Subir código
git push -u origin main
```

---

## 🎯 Instalar el Plugin (Usuarios)

Una vez publicado en GitHub, CUALQUIERA puede instalarlo con:

```bash
/plugin install agent007@TU-USUARIO/agent007 --scope user
```

Reemplaza `TU-USUARIO` con tu username de GitHub.

**Ejemplo**: Si tu usuario es `sebasing`, el comando es:
```bash
/plugin install agent007@sebasing/agent007 --scope user
```

---

## 📊 ¿Qué Obtienen los Usuarios?

Después de instalar, tienen acceso a:

### Skills Disponibles (17)

```bash
/agent007:consult "pregunta"              # Consulta inteligente
/agent007:architecture-review             # Review de arquitectura
/agent007:api-design-principles           # Principios de API
/agent007:resilience-patterns             # Patrones de resiliencia
/agent007:frontend-design                 # Diseño frontend
/agent007:review                          # Code review
/agent007:plan                            # Planificación
/agent007:tdd                             # Test-Driven Development
# ... y 9 skills más
```

### Agentes Expertos (5)

- **backend-db-expert** (Opus) - APIs, NestJS, databases
- **frontend-ux-expert** (Sonnet) - React, Next.js, UX
- **platform-expert** (Sonnet) - CI/CD, testing, Docker
- **product-expert** (Opus) - Product discovery
- **security-expert** (Opus) - OWASP, seguridad

---

## 🔄 Actualizar el Plugin

### Cuando Haces Cambios

```bash
cd /Users/sebasing/Projects/Agent007

# Hacer cambios...

# Actualizar versión en VERSION
echo "2.1.0" > VERSION

# Actualizar .claude-plugin/plugin.json (version: "2.1.0")

# Commit y push
git add .
git commit -m "v2.1.0 - [descripción de cambios]"
git tag v2.1.0
git push origin main --tags
```

### Usuarios Actualizan

```bash
/plugin update agent007
```

---

## ✅ Verificar que Todo Funciona

### 1. Verificar plugin.json

```bash
cat .claude-plugin/plugin.json
```

Debe tener:
- `"name": "agent007"`
- `"version": "2.0.0"`
- `"repository": "https://github.com/TU-USUARIO/agent007.git"`

### 2. Probar Instalación Local (ANTES de publicar)

```bash
# En otro proyecto
cd ~/Projects/OtroProyecto

# Cargar plugin local
claude --plugin-dir /Users/sebasing/Projects/Agent007

# Probar skill
/agent007:consult "test"
```

Si funciona localmente, funcionará cuando lo publiques.

---

## 🎓 Siguiente Paso

**Compartir con tu Equipo**:

1. Sube a GitHub (pasos arriba)
2. Comparte el comando de instalación:
   ```bash
   /plugin install agent007@TU-USUARIO/agent007 --scope user
   ```
3. Tu equipo lo instala en segundos
4. Disponible en TODOS sus proyectos automáticamente

---

## 📞 Soporte

- **GitHub Issues**: https://github.com/TU-USUARIO/agent007/issues
- **README**: Documentación completa
- **INSTALLATION.md**: Guía para usuarios

---

## 🎉 ¡Eso es Todo!

Agent007 está listo para:
- ✅ Publicarse en GitHub
- ✅ Instalarse como plugin de Claude Code
- ✅ Usarse en múltiples proyectos
- ✅ Compartirse con tu equipo

**Siguiente acción**: Ejecutar los comandos git del Paso 1 y 3.
