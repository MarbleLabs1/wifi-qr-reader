# Packaging

## AUR (Arch Linux) — ready, just needs a tag

`PKGBUILD` is set to build from a GitHub release tag (`v1.0.0`). To publish:

1. Tag and push a release: `git tag v1.0.0 && git push --tags`, then create
   the GitHub release from that tag (or the tarball URL in `PKGBUILD` won't
   resolve).
2. Fill in `sha256sums` (currently `SKIP`) by running `updpkgsums` from the
   `packaging/` directory once the tarball exists.
3. Push to a new AUR git repo named `wifi-qr-reader` (see the
   [AUR submission guide](https://wiki.archlinux.org/title/AUR_submission_guidelines)).

## Flatpak / Flathub — manifest scaffolded, two things still needed

`io.github.marbleceo.WifiQrReader.json` has the right shape (runtime,
permissions, install steps) but two placeholders need real values before it
builds:

1. **`zbar` module's `sha256`** — currently `REPLACE_WITH_ACTUAL_SHA256`.
   Download the source tarball at the `url` already in the manifest and run
   `sha256sum` on it.
2. **`python3-requirements` module's sources** — currently a comment
   placeholder. Generate the real, pinned dependency list with
   [flatpak-pip-generator](https://github.com/flatpak/flatpak-builder-tools/tree/master/pip):

   ```sh
   python3 flatpak-pip-generator opencv-python pyzbar PyQt5
   ```

   That prints a `python3-requirements.json` module with every dependency's
   exact source URL and hash — paste it in place of the placeholder module.

   This step needs live network access and the actual `flatpak-builder`
   toolchain, so it wasn't run in the environment these files were drafted
   in — do it once on a machine with Flatpak installed, then:

   ```sh
   flatpak-builder --user --install build-dir packaging/io.github.marbleceo.WifiQrReader.json
   flatpak run io.github.marbleceo.WifiQrReader
   ```

Once it builds and runs locally, submission to Flathub is: fork
`flathub/flathub`, open a PR adding this manifest under a new
`io.github.marbleceo.WifiQrReader` repo, and their CI takes it from there.

### Why `--device=all` and `flatpak-spawn --host`

- The webcam needs `--device=all` (Flatpak has no portal for arbitrary
  `/dev/video*` access the way it does for the camera *portal* used by some
  toolkits — this app doesn't use that portal, so it needs the device
  directly).
- `nmcli`/`systemctl` aren't inside the sandbox. `wifi_qr_reader/app.py`'s
  `host_command()` helper prefixes those calls with `flatpak-spawn --host`
  when `FLATPAK_ID` is set, so they run against the real system instead —
  this needs the `--talk-name=org.freedesktop.Flatpak` permission already in
  the manifest. Outside Flatpak (pip install, AUR) it's a no-op.
