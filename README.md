# Red Engine V2 - Enhanced System

This is the enhanced Red Engine V2 system with new modules for lead finding, affiliate updating, game cloning, config vault, and scheduling.

## New Modules

### 1. LeadFinder Module (`modules/lead_finder/`)
- **Purpose**: Search for job leads and extract contact information
- **Features**:
  - Web search integration (DuckDuckGo)
  - Email extraction from search results
  - Caching of search results
  - Export capabilities (JSON, CSV)
- **CLI Command**: `lead_finder <query> [category]`
- **GUI Tab**: 🔍 Lead Finder

### 2. AffiliateUpdater Module (`modules/affiliate_updater/`)
- **Purpose**: Automate monthly affiliate landing page updates
- **Features**:
  - Generate HTML affiliate links
  - Video integration
  - GitHub Pages deployment
  - Backup creation
- **CLI Command**: `affiliate_update`
- **GUI Tab**: 📈 Affiliate Updater

### 3. GameCloner Module (`modules/game_cloner/`)
- **Purpose**: Clone and retheme game templates from external sources
- **Features**:
  - GitHub template cloning
  - Custom asset replacement
  - Ad banner injection
  - Metadata management
- **CLI Command**: `game_clone [template_url] [game_name]`
- **GUI Tab**: 🎮 Game Cloner

### 4. ConfigVault Module (`modules/config_vault/`)
- **Purpose**: Secure key management with encryption
- **Features**:
  - AES-256-GCM encryption
  - Categorized key storage
  - Access tracking
  - Backup/restore functionality
  - OpenCode yellow highlighting support
- **CLI Command**: `config_vault [list|get <key>|add <key> <value> <category> <description>|highlighted]`
- **GUI Tab**: 🔑 Config Vault

### 5. MonthlyScheduler Module (`modules/scheduler/`)
- **Purpose**: Automated monthly task scheduling
- **Features**:
  - Monthly, weekly, and daily task scheduling
  - Task execution with error handling
  - Status tracking
  - Task management
- **CLI Command**: `scheduler [status|monthly|weekly|daily|add <name> <type> <parameters>]`
- **GUI Tab**: 📊 System Status

### 6. GUI Module (`modules/gui/`)
- **Purpose**: Tkinter-based graphical interface
- **Features**:
  - Tabbed interface for all modules
  - Interactive forms and controls
  - Real-time status updates
  - File browsing
  - Export/import functionality
- **CLI Command**: `gui` (launches GUI)

## System Integration

All new modules are integrated into the existing RedEngine architecture:

1. **Module Registration**: Each module is registered with the engine in `init_all()`
2. **CLI Commands**: New commands are added to the COMMANDS dictionary
3. **Config Integration**: Modules use the existing Config system for settings
4. **Logging**: All modules use the engine's logging system

## Usage Examples

### Lead Finder
```bash
# Search for jobs
red_engine lead_finder "music animator or crypto developer" crypto

# Get cached leads
red_engine lead_finder --list crypto
```

### Affiliate Updater
```bash
# Update monthly landing page
red_engine affiliate_update
```

### Game Cloner
```bash
# Clone and retheme a game
red_engine game_clone "https://github.com/example/clean-flappy-bird-template" "Flappy_Jessica_Rabbit"
```

### Config Vault
```bash
# List all keys
red_engine config_vault list

# Add a new key
red_engine config_vault add YOUTUBE_API_KEY "your_key_here" "youtube" "YouTube API key for video uploads"

# Get a key
red_engine config_vault get YOUTUBE_API_KEY

# Get highlighted keys for OpenCode
red_engine config_vault highlighted
```

### Scheduler
```bash
# Check scheduler status
red_engine scheduler status

# Run monthly tasks
red_engine scheduler monthly

# Run weekly tasks
red_engine scheduler weekly

# Run daily tasks
red_engine scheduler daily

# Add a new task
red_engine scheduler add "Monthly Affiliate Update" "affiliate_update" "{\"links\": {\"Product A\": \"https://example.com/a\"}}"
```

### GUI
```bash
# Launch GUI
red_engine gui
```

## Configuration

### Environment Variables
- `GITHUB_TOKEN`: For GitHub Pages deployment
- `AD_CLIENT_ID_SECRET`: For ad network integration
- `YOUTUBE_API_KEY`: For YouTube video uploads
- `REPLICATE_API_KEY`: For video rendering
- `LUNO_API_KEY_ID`, `LUNO_API_KEY_SECRET`: For Luno exchange
- `BINANCE_API_KEY`, `BINANCE_SECRET_KEY`: For Binance exchange

### Configuration Files
- `config/config.json`: Main configuration
- `modules/config_vault/config_vault.json`: Encrypted key vault
- `modules/config_vault/config_key.key`: Encryption key
- `modules/lead_finder/leads_cache.json`: Lead search cache
- `modules/scheduler/scheduler_state.json`: Scheduler state
- `modules/scheduler/scheduled_tasks.json`: Scheduled tasks

## Security

The ConfigVault module uses AES-256-GCM encryption to secure sensitive keys. The encryption key is stored in `config_key.key` and should not be committed to version control.

## Development

To add new modules:
1. Create a new directory in `modules/`
2. Implement the module's `__init__.py` with the required interface
3. Register the module in `init_all()` in `main.py`
4. Add CLI commands to the COMMANDS dictionary
5. Update the GUI if needed

## Testing

Run the existing tests to ensure compatibility:
```bash
# Run tests (if available)
python -m pytest

# Test individual modules
python -c "from modules.lead_finder import LeadFinder; print('LeadFinder imported successfully')"
python -c "from modules.affiliate_updater import AffiliateUpdater; print('AffiliateUpdater imported successfully')"
python -c "from modules.game_cloner import GameCloner; print('GameCloner imported successfully')"
python -c "from modules.config_vault import ConfigVault; print('ConfigVault imported successfully')"
python -c "from modules.scheduler import MonthlyScheduler; print('MonthlyScheduler imported successfully')"
```

## License

This system is part of Red Engine V2 and is licensed under the same terms as the main project.
