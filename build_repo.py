import os
import glob
import io
import tarfile
import hashlib
import gzip
import bz2
import lzma
import json
import re

REPO_URL = "https://fewly11.github.io/"
ORIGIN = "Fewly Repo"
LABEL = "Fewly Repo (Dopamine Rootless)"
SUITE = "stable"
VERSION = "2.0"
CODENAME = "ios"
ARCHITECTURES = "iphoneos-arm64 iphoneos-arm"
COMPONENTS = "main"
DESCRIPTION = "Kho tweak & tiện ích hỗ trợ Jailbreak Dopamine Rootless (iOS 15 - 16.6.5) & Rootful"

def hash_file(filepath):
    md5 = hashlib.md5()
    sha1 = hashlib.sha1()
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            md5.update(chunk)
            sha1.update(chunk)
            sha256.update(chunk)
    return md5.hexdigest(), sha1.hexdigest(), sha256.hexdigest(), os.path.getsize(filepath)

def extract_control_from_deb(deb_path):
    try:
        with open(deb_path, 'rb') as f:
            magic = f.read(8)
            if magic != b'!<arch>\n':
                return None
            while True:
                header = f.read(60)
                if len(header) < 60:
                    break
                name = header[:16].strip().decode('ascii', errors='ignore')
                size_str = header[48:58].strip().decode('ascii', errors='ignore')
                size = int(size_str)
                if 'control.tar' in name:
                    control_data = f.read(size)
                    with tarfile.open(fileobj=io.BytesIO(control_data)) as tar:
                        for member in tar.getmembers():
                            if member.name.endswith('control') and not member.isdir():
                                cf = tar.extractfile(member)
                                if cf:
                                    return cf.read().decode('utf-8', errors='ignore')
                    break
                else:
                    f.seek(size, 1)
                if size % 2 == 1:
                    f.seek(1, 1)
    except Exception as e:
        print(f"Error reading {deb_path}: {e}")
    return None

def parse_control_block(text):
    fields = {}
    current_key = None
    for line in text.splitlines():
        if not line:
            continue
        if line[0] in (' ', '\t') and current_key:
            fields[current_key] += '\n' + line
        elif ':' in line:
            parts = line.split(':', 1)
            current_key = parts[0].strip()
            fields[current_key] = parts[1].strip()
    return fields

def build_repo():
    print("Scanning debs directory...")
    deb_files = sorted(glob.glob("debs/*.deb"))
    print(f"Found {len(deb_files)} deb files.")
    
    # Load fallback metadata from existing Packages if available
    fallback_map = {}
    if os.path.exists("Packages"):
        with open("Packages", "r", encoding="utf-8", errors="ignore") as f:
            raw = f.read()
            for block in raw.split("\n\n"):
                block = block.strip()
                if not block:
                    continue
                parsed = parse_control_block(block)
                pkg = parsed.get("Package")
                fn = parsed.get("Filename", "")
                base_deb = os.path.basename(fn)
                if base_deb:
                    fallback_map[base_deb] = parsed
                if pkg:
                    fallback_map[pkg] = parsed

    package_entries = []
    json_packages = []

    for deb_path in deb_files:
        deb_basename = os.path.basename(deb_path)
        md5, sha1, sha256, size = hash_file(deb_path)
        
        control_text = extract_control_from_deb(deb_path)
        fields = parse_control_block(control_text) if control_text else {}
        
        # Merge with fallback if missing fields
        fallback = fallback_map.get(deb_basename, {})
        for k, v in fallback.items():
            if k not in fields or not fields[k]:
                fields[k] = v

        if not fields.get("Package"):
            fields["Package"] = deb_basename.replace(".deb", "").lower().replace("_", ".")
        if not fields.get("Name"):
            fields["Name"] = fields.get("Package", deb_basename)
        if not fields.get("Version"):
            fields["Version"] = "1.0"
        if not fields.get("Section"):
            fields["Section"] = "Tweaks"
        if not fields.get("Description"):
            fields["Description"] = f"Tweak {fields['Name']} cho iOS / Dopamine Jailbreak"
        if not fields.get("Author") and fields.get("Maintainer"):
            fields["Author"] = fields["Maintainer"]
        elif not fields.get("Author"):
            fields["Author"] = "fewly"

        orig_arch = fields.get("Architecture", "iphoneos-arm")
        
        # Ensure Dopamine rootless compatibility:
        # Sileo on Dopamine checks for iphoneos-arm64
        # We will create an iphoneos-arm64 entry and if different, an iphoneos-arm entry
        architectures_to_build = ["iphoneos-arm64"]
        if orig_arch != "iphoneos-arm64":
            architectures_to_build.append("iphoneos-arm")

        for target_arch in architectures_to_build:
            entry_fields = dict(fields)
            entry_fields["Architecture"] = target_arch
            entry_fields["Filename"] = f"./debs/{deb_basename}"
            entry_fields["Size"] = str(size)
            entry_fields["MD5sum"] = md5
            entry_fields["SHA1"] = sha1
            entry_fields["SHA256"] = sha256
            
            # Format Package entry
            lines = []
            # Preferred order of keys
            key_order = [
                "Package", "Name", "Version", "Architecture", "Description", 
                "Maintainer", "Author", "Section", "Depends", "Conflicts", 
                "Replaces", "Installed-Size", "Depiction", "Tag", 
                "Filename", "Size", "MD5sum", "SHA1", "SHA256"
            ]
            for key in key_order:
                if key in entry_fields and entry_fields[key]:
                    lines.append(f"{key}: {entry_fields[key]}")
            for key, val in entry_fields.items():
                if key not in key_order and val:
                    lines.append(f"{key}: {val}")
            
            package_entries.append("\n".join(lines))

        # Store in json_packages for web app
        json_packages.append({
            "package": fields.get("Package"),
            "name": fields.get("Name"),
            "version": fields.get("Version"),
            "section": fields.get("Section", "Tweaks"),
            "architecture": "iphoneos-arm64 (Dopamine) / iphoneos-arm",
            "author": fields.get("Author", fields.get("Maintainer", "Fewly")),
            "description": fields.get("Description", ""),
            "size": size,
            "filename": f"debs/{deb_basename}",
            "deb": deb_basename,
            "dopamine_ready": True
        })

    # Write Packages
    packages_content = "\n\n".join(package_entries) + "\n"
    packages_bytes = packages_content.encode("utf-8")
    
    with open("Packages", "wb") as f:
        f.write(packages_bytes)
    print(f"Written Packages ({len(packages_bytes)} bytes)")

    # Write Packages.gz
    with gzip.open("Packages.gz", "wb") as f:
        f.write(packages_bytes)
    print("Written Packages.gz")

    # Write Packages.bz2
    with bz2.open("Packages.bz2", "wb") as f:
        f.write(packages_bytes)
    print("Written Packages.bz2")

    # Write Packages.xz
    with lzma.open("Packages.xz", "wb") as f:
        f.write(packages_bytes)
    print("Written Packages.xz")

    # Write packages.json
    with open("packages.json", "w", encoding="utf-8") as f:
        json.dump(json_packages, f, ensure_ascii=False, indent=2)
    print(f"Written packages.json ({len(json_packages)} items)")

    # Write sileo-featured.json
    featured = {
        "class": "FeaturedBannersView",
        "itemSize": "{300, 140}",
        "itemCornerRadius": 12,
        "banners": [
            {
                "title": "Fewly Repo - Dopamine Rootless",
                "package": "com.opa334.choicy",
                "url": f"{REPO_URL}now/fewly.png",
                "hideShadow": False
            },
            {
                "title": "SnowBoard - Giao diện & Biểu tượng",
                "package": "com.spark.snowboard",
                "url": f"{REPO_URL}now/fewly.png",
                "hideShadow": False
            },
            {
                "title": "Atria - Tùy biến màn hình chính",
                "package": "me.lau.atria",
                "url": f"{REPO_URL}now/fewly.png",
                "hideShadow": False
            },
            {
                "title": "YouTube Reborn & Cercube",
                "package": "youtube-reborn",
                "url": f"{REPO_URL}now/fewly.png",
                "hideShadow": False
            }
        ]
    }
    with open("sileo-featured.json", "w", encoding="utf-8") as f:
        json.dump(featured, f, indent=2)
    print("Written sileo-featured.json")

    # Update index.html static packages fallback
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            html = f.read()
        marker = "<!-- STATIC_PACKAGES_DATA -->"
        script_injection = f'<script id="staticData">window.__STATIC_PACKAGES__ = {json.dumps(json_packages, ensure_ascii=False)};</script>'
        if marker in html:
            parts = html.split(marker)
            # if already contains static script before next tag
            html = re.sub(r'<script id="staticData">.*?</script>', script_injection, html, flags=re.DOTALL)
        elif '<script src="js/app.js"></script>' in html:
            html = html.replace('<script src="js/app.js"></script>', f'{script_injection}\n  <script src="js/app.js"></script>')
            with open("index.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("Injected static packages fallback into index.html")

    # Generate Release file
    release_files = ["Packages", "Packages.gz", "Packages.bz2", "Packages.xz"]
    
    md5_entries = []
    sha1_entries = []
    sha256_entries = []

    for fn in release_files:
        fmd5, fsha1, fsha256, fsize = hash_file(fn)
        md5_entries.append(f" {fmd5} {fsize} {fn}")
        sha1_entries.append(f" {fsha1} {fsize} {fn}")
        sha256_entries.append(f" {fsha256} {fsize} {fn}")

    release_content = f"""Origin: {ORIGIN}
Label: {LABEL}
Suite: {SUITE}
Version: {VERSION}
Codename: {CODENAME}
Architectures: {ARCHITECTURES}
Components: {COMPONENTS}
Description: {DESCRIPTION}
MD5Sum:
{chr(10).join(md5_entries)}
SHA1:
{chr(10).join(sha1_entries)}
SHA256:
{chr(10).join(sha256_entries)}
"""
    with open("Release", "w", encoding="utf-8") as f:
        f.write(release_content)
    print("Written Release file successfully!")

if __name__ == "__main__":
    build_repo()
