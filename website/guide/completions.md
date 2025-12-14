# Shell Completions

spectra provides shell completion scripts for Bash, Zsh, and Fish shells. These enable tab-completion for commands, options, and file paths.

## Quick Setup

The easiest way to enable completions is to evaluate them dynamically.

::: code-group

```bash [Bash]
# Add to ~/.bashrc
eval "$(spectra --completions bash)"
```

```bash [Zsh]
# Add to ~/.zshrc
eval "$(spectra --completions zsh)"
```

```fish [Fish]
# Add to ~/.config/fish/config.fish
spectra --completions fish | source
```

:::

Then restart your shell or source the config file.

## Manual Installation

### Bash

**Option 1: User-level installation**

```bash
mkdir -p ~/.local/share/bash-completion/completions
spectra --completions bash > ~/.local/share/bash-completion/completions/spectra
```

**Option 2: System-wide installation (requires sudo)**

```bash
sudo spectra --completions bash > /etc/bash_completion.d/spectra
```

**Option 3: Copy from package**

```bash
cp /path/to/spectra/completions/spectra.bash \
   ~/.local/share/bash-completion/completions/spectra
```

### Zsh

**Option 1: User-level installation**

```bash
mkdir -p ~/.zsh/completions
spectra --completions zsh > ~/.zsh/completions/_spectra

# Add to ~/.zshrc (before compinit):
fpath=(~/.zsh/completions $fpath)
autoload -Uz compinit && compinit
```

**Option 2: Oh My Zsh**

```bash
spectra --completions zsh > ~/.oh-my-zsh/completions/_spectra
```

### Fish

**Option 1: User-level installation**

```bash
spectra --completions fish > ~/.config/fish/completions/spectra.fish
```

**Option 2: Symlink from package**

```bash
ln -s /path/to/spectra/completions/spectra.fish \
   ~/.config/fish/completions/
```

## Completion Features

The completion scripts provide intelligent completions for:

### Options

```bash
spectra --<TAB>
--config      --epic        --execute     --export      --help
--interactive --jira-url    --markdown    --no-color    --no-confirm
--phase       --project     --story       --validate    --verbose
--version     --completions
```

### File Paths

```bash
# Markdown files for --markdown
spectra --markdown <TAB>
EPIC.md  README.md  docs/

# Config files for --config
spectra --config <TAB>
.spectra.yaml  config.toml

# JSON files for --export
spectra --export <TAB>
results.json  output.json
```

### Phase Choices

```bash
spectra --phase <TAB>
all  descriptions  subtasks  comments  statuses
```

### Shell Types

```bash
spectra --completions <TAB>
bash  zsh  fish
```

## Troubleshooting

### Completions Not Working in Bash

1. Ensure bash-completion is installed:

::: code-group

```bash [Ubuntu/Debian]
sudo apt install bash-completion
```

```bash [macOS]
brew install bash-completion@2
```

:::

2. Source bash-completion in `~/.bashrc`:

```bash
[[ -r "/usr/share/bash-completion/bash_completion" ]] && \
  source "/usr/share/bash-completion/bash_completion"
```

### Completions Not Working in Zsh

1. Ensure compinit is loaded:

```bash
autoload -Uz compinit && compinit
```

2. Rebuild completion cache:

```bash
rm ~/.zcompdump*
compinit
```

### Completions Not Working in Fish

1. Check the file is in the correct location:

```bash
ls ~/.config/fish/completions/spectra.fish
```

2. Reload completions:

```fish
complete -c spectra -e  # Clear existing
source ~/.config/fish/completions/spectra.fish
```

## Updating Completions

When you update spectra, regenerate completions to get new options:

```bash
# Bash
spectra --completions bash > ~/.local/share/bash-completion/completions/spectra

# Zsh
spectra --completions zsh > ~/.zsh/completions/_spectra
rm ~/.zcompdump*  # Clear cache

# Fish
spectra --completions fish > ~/.config/fish/completions/spectra.fish
```

## Programmatic Access

You can also access completion scripts programmatically:

```python
from spectra.cli import get_completion_script, SUPPORTED_SHELLS

# Get list of supported shells
print(SUPPORTED_SHELLS)  # ['bash', 'zsh', 'fish']

# Get a specific script
bash_script = get_completion_script('bash')
```

