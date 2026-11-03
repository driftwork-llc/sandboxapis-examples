# How to publish this folder as a public repository

This folder is the complete contents of a public repository. It is not a
subdirectory of one: the `README.md` beside this file is the repository's front
page, and `.github/ISSUE_TEMPLATE/` only works at a repository root.

**Target: `https://github.com/driftwork-llc/sandboxapis-examples`, public.**

Four MCP directories are blocked today for one reason only: they want a public
GitHub repository URL under an owner we control. This is that repository.

## The one rule

**Never create it under the founder's personal account, or under any other personal
account.** Every directory listing renders the repository owner. A personal handle
there puts a person's name on the product's public identity in a dozen places at
once, and taking it back later means asking each directory to re-index a moved
repository. The owner is the company: Driftwork LLC.

## Step 0, first: a GitHub account for the brand

This is the step that is easy to skip and expensive to undo. A GitHub
organisation still needs a human account to own it, and that account is what
appears as:

- the author of the pull requests to the awesome-mcp-servers lists, publicly and
  permanently, in a repository with 95,800 stars;
- the GitHub identity that signs in to Glama, which checks write access to the
  repository through GitHub OAuth before it will list it;
- the `maintainers` entry in `glama.json`;
- the contact on a Docker MCP Catalog pull request.

So create a new GitHub account for the brand before creating the organisation,
and use it for all of it:

1. Sign out, or use a second browser profile.
2. Create an account at https://github.com/signup with the email
   `team@sandboxapis.dev` (it routes to the founder's inbox already).
3. Suggested username: `sandboxapis`, or `driftwork-team` if that is taken. Set
   the profile name to `SandboxAPIs` and the company to `Driftwork LLC`. Leave the
   bio to the product.
4. Turn on two-factor authentication immediately. GitHub requires it for
   organisation owners.

Everything below is done as that account.

## Step 1: the organisation

1. Go to https://github.com/organizations/plan and choose the **Free** plan.
2. **Organization account name:** `driftwork-llc` (the founder renamed an existing empty organisation to it on 2026-10-02; the plain name is held by a dormant user account)
   and tell the session, because the repository URL appears in every submission
   file in `marketing/mcp-promotion/` and in the awesome-list lines.
3. **Contact email:** `team@sandboxapis.dev`.
4. **This organization belongs to:** a business or institution. Business name
   `Driftwork LLC`.
5. Skip the invite step.
6. In **Settings, Profile**: display name `Driftwork LLC`, email
   `team@sandboxapis.dev`, URL `https://sandboxapis.dev`. The organisation profile
   is public, so keep it to the company. No personal name, no location beyond
   Arizona if you want one at all.
7. In **Settings, Member privileges**: leave repository creation to owners.

## Step 2: the repository

1. From the organisation page: **New repository**.
2. **Repository name:** `sandboxapis-examples`.

   Why not plain `examples`: the slug is the listing. The awesome-mcp-servers
   entry format is `[owner/repo](url)`, mcp.so asks for a repository URL and
   nothing else, and Glama infers the display name from the repository unless
   `glama.json` overrides it. `driftwork-llc/examples` tells a reader nothing and
   carries none of the product name that is on npm, in the MCP registry and in the
   docs. `driftwork-llc/sandboxapis-examples` reads correctly everywhere, including in
   the forms that drop the description. It also leaves the generic `examples` slug
   free if Driftwork ever ships a second product.
3. **Description:**

   ```
   Runnable examples for SandboxAPIs: the agent eval pack, three agent tutorials, and the MCP server recipes.
   ```
4. **Public.** Do not add a README, a .gitignore or a licence: they are in this
   folder already and GitHub's versions would conflict with the first push.
5. Create it.

## Step 3: push this folder

From a copy of this folder, outside the private monorepo. Copy it out first so a
stray `git init` cannot touch the monorepo's history:

```bash
cp -R /path/to/sandboxapis/public/examples-repo ~/sandboxapis-examples
cd ~/sandboxapis-examples
rm PUBLISH.md                      # this file is instructions, not content
git init -b main
git add -A
git commit -m "Runnable examples: the eval pack, three agent tutorials, and the MCP recipes"
git remote add origin https://github.com/driftwork-llc/sandboxapis-examples.git
git push -u origin main
```

Push as the brand account. If `git push` authenticates as a personal account from a
cached credential, clear it first (`gh auth switch`, or use a token for the brand
account) and check with `git log -1 --format='%an %ae'` before pushing, because
the commit author is public too. Set the local identity if it is wrong:

```bash
git config user.name "SandboxAPIs team"
git config user.email "team@sandboxapis.dev"
```

## Step 4: three settings, then it is ready for the directories

1. **Issues on.** Settings, Features, Issues. This is the part the directories are
   really asking for: a place a user can file a bug that is not an email address.
2. **Topics.** On the repository home page, next to About, add:
   `mcp`, `model-context-protocol`, `mcp-server`, `testing`, `sandbox`,
   `fixtures`, `agent-evaluation`, `github-api`, `jira`, `slack`.
   Several directories read them.
3. **`glama.json`.** Replace `REPLACE_WITH_BRAND_GITHUB_HANDLE` with the brand
   account's GitHub username and push. Glama will not accept a maintainer it
   cannot match to the account submitting the listing.

Then check these, because each one is a field a directory reads:

- The licence badge shows MIT on the repository home page. Glama runs licence
  detection during indexing and Docker's catalog requires a permissive licence.
- `npx -y @sandboxapis/mcp` in a fresh directory starts clean over stdio. Several
  scanners run exactly that.
- The three tutorial scripts and `evals/run.mjs` still pass. They were verified
  against the pinned hosts on 2026-10-02: 53 of 53 eval items correct, and all
  three tutorial scripts printed `ok`.

## What must never go in here

Nothing from `packages/` except what is already published on npm. Specifically
not `packages/generator`, `packages/compiler`, `packages/canon`,
`packages/themes`, any renderer, any compiled artifact, the pipeline, or anything
under `supabase/`. No keys, no `.env` of any kind, and no snapshot artifact files.
The engine repository stays private, and none of the directories asks for it.

## Then hand it back

Tell the session the final repository URL. `marketing/mcp-promotion/PLAN.md` lists
what can be submitted the same hour, and every submission file there is written
against this URL.
