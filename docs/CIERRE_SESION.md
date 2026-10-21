# Cierre de sesión — Fabricante de Ideas

Sin Claude Code ni worktree: los commits se hacen en `~/proyectos/FabricanteDeIdeas`.

## 1. Lo que entrega el Project
Archivos completos, como descargables: la sesión nueva `AAMMDD_sesion.md` (`docs/bitacora/`), la
`BITACORA.md` (`docs/`) y lo que cambió (`docs/PROYECTOS.md`, archivos del kit en `kit/…`, las
instrucciones). Si el kit cambia de versión, entrega también el zip `AAMMDD_kit_proyecto_vX_Y.zip`.

## 2. Pasos de Tomek
**1. Descargar** todo a `D:\Descargas`.

**2. Poner el repo al día (terminal SSH)**
```bash
ssh orangepi@192.168.1.163
cd ~/proyectos/FabricanteDeIdeas
git pull
```

**3. Copiar (PowerShell)**, una línea por archivo, con la ruta de destino que dé el Project:
```powershell
scp D:\Descargas\BITACORA.md orangepi@192.168.1.163:~/proyectos/FabricanteDeIdeas/docs/BITACORA.md
scp D:\Descargas\AAMMDD_sesion.md orangepi@192.168.1.163:~/proyectos/FabricanteDeIdeas/docs/bitacora/
```

**4. Commit y push (terminal SSH)**
```bash
cd ~/proyectos/FabricanteDeIdeas
git status -sb
git add docs/BITACORA.md docs/bitacora/AAMMDD_sesion.md
git commit -m "Cierre AAAA-MM-DD: <tema>"
git push origin main
git log --oneline -1
```

**5. Knowledge (siempre el último):** reemplaza `BITACORA.md`, quita la sesión anterior y sube la
nueva, y sube lo demás que cambió.
