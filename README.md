# envforge

> CLI tool to snapshot and restore local environment variables across projects

---

## Installation

```bash
pip install envforge
```

---

## Usage

**Save a snapshot of your current environment:**

```bash
envforge save myproject
```

**Restore a saved snapshot:**

```bash
envforge restore myproject
```

**List all saved snapshots:**

```bash
envforge list
```

**Delete a snapshot:**

```bash
envforge delete myproject
```

Snapshots are stored locally in `~/.envforge/` and can be shared across terminals or machines.

---

## Example

```bash
$ export API_KEY=abc123
$ export DEBUG=true
$ envforge save dev-env

✔ Snapshot 'dev-env' saved (2 variables)

$ envforge restore dev-env

✔ Environment restored from 'dev-env'
```

---

## License

MIT © [envforge contributors](https://github.com/envforge/envforge)