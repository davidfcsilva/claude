# Module 3: Shell & Bash Basics

**Timebox:** 30 minutes

---

## What You Know

As a Windows Admin, you work in two shells:

- **PowerShell** — object-based, cmdlet-driven, .NET-backed
- **CMD (command.com)** — legacy text pipeline, barely used

```powershell
# Common PowerShell patterns
Get-Service | Where-Object Status -eq 'Running' | Select-Object Name
Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 10
Get-Command -Module Microsoft.PowerShell.Management
Get-ChildItem C:\Windows\System32 | Where-Object Extension -eq '.dll'
```

## The Shift

Linux has **one shell** (Bash) for everything — no PowerShell vs CMD split. Bash is **text-driven**, not object-driven. You pipe **text** between commands. The magic is in chaining small, focused tools instead of large, all-in-one cmdlets.

```bash
# Linux shell: text pipeline, one tool does one thing well
ps aux | grep ssh | awk '{print $2, $11}' | sort -u
```

### Your First 20 Commands

| PowerShell | Linux Bash | What It Does |
|------------|------------|---------|------|------|
| `Get-Command` | `which` / `whereis` | Find a command's location |
| `Get-ChildItem C:\` | `ls /` | List directory contents |
| `cd C:\Windows` | `cd /usr` | Change directory |
| `mkdir C:\Temp\test` | `mkdir /tmp/test` | Create directory |
| `cp file1 file2` | `cp file1 file2` | Copy a file |
| `mv file1 file2` | `mv file1 file2` | Move/rename a file |
| `rm file1` | `rm file1` | Delete a file |
| `rm -Recurse dir1` | `rm -r dir1` | Delete a directory tree |
| `Get-Content file` | `cat file` | Display file contents |
| `Get-Content file | Select-Object -First 10` | `head -10 file` | First 10 lines |
| `Get-Content file | Select-Object -Last 10` | `tail -10 file` | Last 10 lines |
| `Get-ChildItem . -Recurse -Filter *.log` | `find . -name "*.log"` | Recursively find files |
| `Get-Process` | `ps aux` | List running processes |
| `Stop-Process -Name foo` | `pkill foo` / `killall foo` | Kill a process |
| `Get-Date` | `date` | Current date/time |
| `whoami` / `Get-Whoami` | `whoami` / `id` | Current user |
| `Clear-Host` | `clear` | Clear the terminal |
| `Get-NetIPAddress` | `ip a` / `ip addr` | Network interfaces |
| `Get-Service` | `systemctl list-units --type=service` | List services |
| `Get-Date | Get-Date` | `date` | Current date/time |

### Path Syntax

| Windows | Linux | Note |
|---------|-------|-----|
| `C:\Program Files\foo.txt` | `/usr/local/foo.txt` | Forward slashes always |
| `C:\Users\david\Documents` | `/home/david/Documents` | No backslashes in bash |
| `C:\` | `/` | Root of everything |
| `.` | `.` | Current directory |
| `..` | `..` | Parent directory |
| `%USERPROFILE%\Documents` | `~/Documents` | Tilde = home directory |
| `$env:TEMP` | `$TMPDIR` or `/tmp` | Environment variables |

### Your Shell Is Your Profile

```bash
# Who am I? (Windows: whoami / Get-WmiObject Win32_ComputerSystem)
whoami
whoami -u                   # UID info
hostname                    # Windows: hostname

# What's my home directory? (Windows: $env:USERPROFILE)
echo $HOME                  # Linux: $HOME (Windows: $env:USERPROFILE)
echo ~                      # Tilde expands to home

# What shell am I using? (Windows: $host.Name)
echo $SHELL                 # Usually /bin/bash
echo $BASH_VERSION           # Bash version

# Environment variables (Windows: Get-ChildItem env:)
env | sort                  # All env vars, sorted
echo $PATH                  # Where commands live (Windows: $env:Path)
```

### Command Syntax

```bash
# Standard format (Windows: cmdlet -Parameter value)
command [OPTIONS] [ARGUMENTS]

# Examples:
cp -v file1 file2           # Verbose copy
ls -lah /etc                # Long listing, hidden files, human sizes
rm -rf /tmp/dirty           # Recursive + force delete
mkdir -p /a/b/c/d           # Create parent dirs as needed
cat -n file.txt             # Show line numbers

# Help (Windows: Get-Help Get-Service)
man cp                      # Manual page (Windows: Get-Help)
cp --help                   # Quick usage (Windows: cp /?)
apropos network             # Search man pages (Windows: Get-Command -Module)
```

### Piping & Redirection

This is where Bash differs most from PowerShell. In PowerShell, you pipe **objects**. In Bash, you pipe **text**.

```bash
# Pipe: text goes from one command's stdout to another's stdin
ps aux | grep sshd          # List processes + filter (Windows: Get-Process | Where-Object)
cat /var/log/syslog | grep error | tail -5  # Chain multiple commands
ls -la /etc | wc -l         # Count lines in ls output

# Redirect stdout to a file (Windows: > in PS also works the same)
ls -la /usr/bin > /tmp/binlist.txt    # Overwrite
cat file.txt >> /tmp/append.txt       # Append

# Redirect stderr to /dev/null (Windows: 2>$null)
ls /nonexistent 2>/dev/null             # Suppress error output

# Pipe to a pager (Windows: Format-Table)
ps aux | less                           # Scroll through output
ps aux | more                           # Page by page

# Here-string (Windows: @'...'@)
grep "error" <<< "some text\nwith error"

# Subshell (Windows: $(...) equivalent)
today=$(date +%F)
echo "Today is $today"
```

### Text Processing Trio

PowerShell has object methods. Bash has three text tools that do everything:

#### `grep` — Find text patterns

```bash
# Find a word in a file (Windows: Select-String)
grep "error" /var/log/syslog

# Case-insensitive + line numbers (Windows: Select-String -CaseSensitive:$false)
grep -in "warning" /var/log/syslog

# Invert match — show lines NOT matching (Windows: Where-Object { $_ -ne $x })
grep -v "^#" /etc/ssh/sshd_config

# Show context around match (Windows: Select-String -Context 2)
grep -C 3 "segfault" /var/log/syslog

# Regular expressions (Windows: Select-String uses PS regex)
grep -E "^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$" /etc/hosts

# Count matches (Windows: Select-String | Measure-Object)
grep -c "denied" /var/log/auth.log
```

#### `awk` — Column-oriented text processing

```bash
# Print specific columns (Windows: Select-Object Column1,Column2)
ps aux | awk '{print $2, $11}'          # PID + command name

# Column math (Windows: Measure-Object -Sum)
ps aux | awk '{sum+=$6} END {print sum/1024 " MB"}'    # Total shared memory

# Filter + format (Windows: Where-Object + Select-Object)
ps aux | awk '$3 > 10 {print $11, $3"%"}'             # Processes using >10% CPU

# Replace text in columns (Windows: -replace)
cat /etc/passwd | awk -F: '{print $1, $7}'             # Username + shell (delimiter = :)
```

#### `sed` — Stream editor

```bash
# Find and replace in a file (Windows: (Get-Content f).replace(a,b) | Set-Content f)
sed -i 's/old-text/new-text/g' file.txt                # In-place replacement

# Delete lines matching a pattern (Windows: Where-Object { $_ -notmatch $x })
sed -i '/^#/d' /etc/ssh/sshd_config                    # Delete comment lines

# Print specific lines (Windows: Select-Object)
sed -n '5,10p' file.txt                                # Lines 5 through 10
```

### Aliases & Shortcuts

```bash
# Create an alias (Windows: New-Alias)
alias ll='ls -lah'
alias gs='git status'
alias ..='cd ..'
alias cls='clear'

# List all aliases (Windows: Get-Alias)
alias

# Make aliases persistent — add to ~/.bashrc
echo "alias ll='ls -lah'" >> ~/.bashrc
source ~/.bashrc

# Check your aliases (Windows: Get-Alias | Format-Table)
alias | grep ll
```

### Wildcards (Globbing)

```bash
# Wildcard matching (Windows: PowerShell * works the same)
ls *.txt              # All .txt files
ls /etc/*conf*        # Anything with "conf" in the name
ls /dev/sd?           # /dev/sda, /dev/sdb, /dev/sdc (single char wildcard)

# Negate (Windows: ? -notlike "pattern*")
ls !(*.log)           # All files except .log (bash 4+)

# Brace expansion (Windows: 1..10 in PS; {1..10})
mkdir test-{a,b,c}    # Creates test-a test-b test-c
ls file-{1,2,3}.txt   # file-1.txt file-2.txt file-3.txt
```

### Tab Completion

```bash
# Linux bash completion (Windows: Tab also works in PS)
# Type part of a path/name then press TAB:
cd /etc/ssh/[TAB]     # Expands to sshd_config or ssh_config
ls /usr/[TAB][TAB]    # Lists all /usr/ subdirectories
ls /etc/ssh/ssh[cTAB] # Completes to ssh_config

# Double TAB to list all completions (Windows: Tab Tab in PS)
ls /etc/ssh/[TAB][TAB]

# History navigation (Windows: Up arrow in PS also works)
up-arrow              # Previous command
down-arrow            # Next command
Ctrl+R                # Search history (type to search)
history               # Full command history
!!                  # Repeat last command
!$                  # Last argument of previous command
!p:2                # Second argument of command matching "p"
```

### Bash vs PowerShell — Key Differences

| Concept | PowerShell | Bash |
|---------|------------|------|
| Truth values | `$true` / `$false` | `0` (success) / `1` (failure) |
| No-match returns | `@()` (empty array) | Empty string (no output) |
| Null value | `$null` | `""` or `$VAR` unset |
| Strings | `'single'` / `"double"` / `@"..."@` | `'single'` (literal) / `"double"` (expand vars) |
| Variables | `$x` (always) | `$x` (in double quotes) / `x` (assignment) |
| Arrays | `@(1,2,3)` | `arr=(1 2 3)` |
| Objects | PSCustomObject, .NET types | None — everything is text |
| Methods | `.ToUpper()`, `.Length` | None — use `awk`, `sed`, `tr` |
| Piping | Objects with properties | Text lines |
| Help | `Get-Help`, `Get-Command` | `man`, `--help`, `apropos` |
| Aliases | `New-Alias` / `Get-Alias` | `alias` / `unalias` |
| History | `$history` | `history` |

### Scripting Basics

```bash
#!/bin/bash
# Shebang — tells the OS to use bash (Windows: # PowerShell requires .ps1)
# Save as hello.sh, make executable: chmod +x hello.sh

# Variables
NAME="World"
echo "Hello, $NAME!"

# Conditionals (Windows: if ($x -eq $y))
if [ -f "/etc/passwd" ]; then
    echo "Password file exists"
elif [ -d "/etc/passwd" ]; then
    echo "Password file is a directory"
else
    echo "Password file not found"
fi

# Loops (Windows: foreach ($x in $y))
for file in /etc/*.conf; do
    echo "Config: $file"
done

# Arrays (Windows: $arr = @(1,2,3))
colors=(red green blue)
echo "${colors[1]}"       # green
echo "${#colors[@]}"      # 3 (array length)

# Functions (Windows: function Name {} )
greet() {
    echo "Hello, $1!"
}
greet "Alice"             # positional param = $1
```

## Hands-On Exercise

```bash
# 1. Find where a command lives
which grep
which python3
which bash

# 2. List files, filter, count
ls -la /etc | grep conf | wc -l

# 3. Find all config files in /usr
find /usr -name "*.conf" -type f | head -20

# 4. Search your command history
history | grep ssh

# 5. Create a test directory tree
mkdir -p /tmp/lab/a/b/c
touch /tmp/lab/a/file1.txt /tmp/lab/a/b/file2.txt
ls -R /tmp/lab

# 6. Chain commands (PowerShell equivalent: Get-Process | Where ... | Sort ... | Select -First)
ps aux | awk '{print $1}' | sort | uniq -c | sort -rh | head -10

# 7. Set an alias and use it
alias ll='ls -lah'
ll /etc/ssh/

# 8. Use grep with context
grep -C 5 "sshd" /var/log/syslog
```

## Mental Model Shift

| PowerShell Mindset | Bash Mindset |
|---------------------|-------------|
| Pipe objects with properties | Pipe text lines |
| `Get-Service | Where { $_.Status -eq "Running" } | Select Name` | `ps aux | grep ssh | awk '{print $1}'` |
| `Get-ChildItem C:\Windows -Recurse -Filter *.dll` | `find /usr -name "*.dll" -type f` |
| `Select-Object` selects columns by name | `awk '{print $N}'` selects columns by number |
| `.ToUpper()`, `.Length`, `.Split()` | `tr`, `sed`, `awk` for text manipulation |
| `Select-String` finds text | `grep` finds text (identical concept) |
| `$env:VAR` accesses env vars | `$VAR` or `${VAR}` |
| `# Comment` | `# Comment` (same) |
| `Get-Help Get-Process` | `man ps` or `ps --help` |
| `Format-Table` formats output | `column -t` or `awk` for column alignment |
| `foreach ($x in $arr)` | `for x in "${arr[@]}"; do` |

**Key takeaway:** Bash is a text pipeline. You chain small tools (`grep`, `awk`, `sed`, `sort`, `uniq`, `cut`) instead of relying on one large cmdlet. Once you understand piping text between focused tools, Bash becomes more flexible and composable than PowerShell for many tasks. Tab completion and history (`Ctrl+R`) make you fast. `/etc` is your source of truth — if you can't find a setting in a GUI, it's in a text file there somewhere.
