# Changelog

## [1.0.0] - 2024-01-15

### Added
- Initial release of Malvryx AV
- Signature-based detection using MD5 hash matching
- YARA rule engine for pattern-based malware detection
- Behavioral monitoring (CPU spikes, Memory usage, Network connections)
- Real-time file watcher with watchdog
- Quarantine system with password-protected ZIP isolation
- Web dashboard with Flask
- One-click Windows installer
- Auto-start with Windows registry
- GitHub Actions CI/CD pipeline
- Render.com deployment support
- Vercel deployment support
- Cloud mode with /tmp storage
- Process monitoring and alerting
- Detection logging system
- EICAR test file for validation

### Security
- Password-protected quarantine (malvryx_2024)
- Zero data collection policy
- All processing done locally
- No cloud uploads

### Performance
- Lightweight: ~50MB RAM usage
- <5% CPU usage during idle
- Multi-threaded scanning
- Efficient file watching with cooldown

### Known Issues
- Some false positives may occur
- Full system scan can be slow on large drives
- Linux support requires additional testing
- YARA rules need to be updated regularly

### Upcoming
- Machine learning detection
- Cloud signature updates
- Mobile version
- Kernel-level protection
