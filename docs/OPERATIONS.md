Operations guide
---

# Database

## Work with backup

Get info about backups:
```shell
sudo -u postgres pgbackrest --stanza=main info
```

Check if the configuration is valid:
```shell
sudo -u postgres pgbackrest --stanza=main check
```

Perform backup:
```shell
sudo -u postgres pgbackrest --stanza=main backup

```
Backups are located in: `/var/lib/pgbackrest/backup`

Restore from backup:
```shell
sudo -u postgres pgbackrest --stanza=main --type=standby restore
```
