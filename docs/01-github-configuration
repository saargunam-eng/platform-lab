


* New SSH key
* New SSH profile
* GitHub scoped to *this* account
* No breakage to your existing GitHub setup


---

# Step-by-step: Separate SSH key + profile for this GitHub account

## STEP 1 — Create a new SSH key (platform-specific)

Use a clearly named key.

```bash
ssh-keygen -t ed25519 -C "platform-github" -f ~/.ssh/id_ed25519_platform
```

When prompted:

* Passphrase → optional (recommended but your call)

This creates:

* `~/.ssh/id_ed25519_platform`
* `~/.ssh/id_ed25519_platform.pub`

---

## STEP 2 — Add the key to your SSH agent

Start agent if needed:

```bash
eval "$(ssh-agent -s)"
```

Add the key:

```bash
ssh-add ~/.ssh/id_ed25519_platform
```

Verify:

```bash
ssh-add -l
```

You should see `id_ed25519_platform`.

---

## STEP 3 — Add SSH config profile (this is the key step)

Edit (or create) SSH config:

```bash
nano ~/.ssh/config
```

Add this **exact block**:

```sshconfig
# Platform GitHub account
Host github-platform
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_platform
  IdentitiesOnly yes
```

Save and exit.

This creates a **separate SSH identity** called `github-platform`.

---

## STEP 4 — Add the public key to GitHub

Copy the public key:

```bash
pbcopy < ~/.ssh/id_ed25519_platform.pub
```

Go to GitHub →
**Settings → SSH and GPG keys → New SSH key**

* Title: `platform-macbook`
* Key type: Authentication
* Paste → Save

---

## STEP 5 — Test the new profile (important)

Run:

```bash
ssh -T git@github-platform
```

Expected:

```
Hi <your-username>! You've successfully authenticated, but GitHub does not provide shell access.
```

If you see the *correct account username* → perfect.

---

## STEP 6 — Configure git to use this profile for platform work

### Option A (recommended): per-repo config

When you create repos for this project, we’ll use the custom host.

Example clone URL:

```bash
git@github-platform:your-username/platform-lab.git
```

Git will automatically use the right key.

---

### Option B (optional): directory-based config (cleaner long-term)

Tell git:

> “Any repo under ~/platform uses this identity.”

Edit global git config:

```bash
git config --global --edit
```

Add:

```ini
[includeIf "gitdir:~/platform/"]
  path = ~/.gitconfig-platform
```

Now create `~/.gitconfig-platform`:

```bash
nano ~/.gitconfig-platform
```

Add:

```ini
[user]
  name = Your Name
  email = your-platform-email@example.com

[url "git@github-platform:"]
  insteadOf = git@github.com:
```

🔥 This is *chef’s kiss* clean.

---

## STEP 7 — Authenticate `gh` CLI with the new account

Run:

```bash
gh auth login
```

Choose:

* GitHub.com
* SSH
* Use existing SSH key
* Select `id_ed25519_platform`

When asked about git protocol → SSH

Verify:

```bash
gh auth status
```

It should show the **new account**.

---

## STEP 8 — Create your workspace and first repo

Now we proceed with zero conflicts.

```bash
mkdir -p ~/platform
cd ~/platform
gh repo create platform-lab --public --clone
cd platform-lab
```

If this works → setup is complete.

---

## Sanity checklist (everything should be true)

* `ssh -T git@github-platform` works
* `gh auth status` shows correct account
* `git remote -v` uses `github-platform`
* No impact to your other GitHub account

---

Once this is done, say **“setup done”** and we’ll immediately:
👉 scaffold `platform-lab`
👉 write the first experiment
👉 get you moving on Day 1 content

You’re doing this the *right* way.
