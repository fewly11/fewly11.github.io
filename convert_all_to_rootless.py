import os
import glob
import io
import shutil
import tarfile
import gzip

def make_ar_header(name, size, mode=0o100644, mtime=0):
    mode_str = oct(mode)[2:]
    h_name = f"{name:<16}"[:16].encode("ascii")
    h_mtime = f"{mtime:<12}"[:12].encode("ascii")
    h_uid = f"{0:<6}"[:6].encode("ascii")
    h_gid = f"{0:<6}"[:6].encode("ascii")
    h_mode = f"{mode_str:<8}"[:8].encode("ascii")
    h_size = f"{size:<10}"[:10].encode("ascii")
    h_end = b"\x60\n"
    return h_name + h_mtime + h_uid + h_gid + h_mode + h_size + h_end

def reroot_path(path):
    p = path.lstrip(".")
    if p.startswith("/"):
        p = p[1:]
    if not p:
        return "."
    if p.startswith("var/jb") or p.startswith("var/mobile"):
        return "./" + p
    prefixes = ("Library", "Applications", "usr", "etc", "System", "bin", "sbin", "var")
    for prefix in prefixes:
        if p == prefix or p.startswith(prefix + "/"):
            return "./var/jb/" + p
    return "./var/jb/" + p

def convert_single_deb(deb_path):
    with open(deb_path, "rb") as f:
        magic = f.read(8)
        if magic != b"!<arch>\n":
            return False, "Not an ar archive"
        members = {}
        while True:
            h = f.read(60)
            if len(h) < 60:
                break
            name = h[:16].strip().decode("ascii", errors="ignore")
            size = int(h[48:58].strip().decode("ascii", errors="ignore"))
            data = f.read(size)
            members[name] = data
            if size % 2 == 1:
                f.seek(1, 1)

    control_keys = [k for k in members.keys() if "control.tar" in k]
    data_keys = [k for k in members.keys() if "data.tar" in k]
    if not control_keys or not data_keys:
        return False, "Missing control.tar or data.tar"

    control_key = control_keys[0]
    data_key = data_keys[0]

    # Process control archive
    new_control_buf = io.BytesIO()
    with tarfile.open(fileobj=io.BytesIO(members[control_key])) as in_tar, \
         tarfile.open(fileobj=new_control_buf, mode="w:gz") as out_tar:
        for m in in_tar.getmembers():
            f = in_tar.extractfile(m) if m.isfile() else None
            content = f.read() if f else b""
            if m.name.endswith("control"):
                text = content.decode("utf-8", errors="ignore")
                new_lines = []
                arch_found = False
                for line in text.splitlines():
                    if line.startswith("Architecture:"):
                        new_lines.append("Architecture: iphoneos-arm64")
                        arch_found = True
                    elif line.startswith("Depends:"):
                        deps = line[8:].strip()
                        deps = deps.replace("mobilesubstrate", "ellekit | mobilesubstrate (>= 0.9.5000)")
                        new_lines.append("Depends: " + deps)
                    else:
                        new_lines.append(line)
                if not arch_found:
                    new_lines.append("Architecture: iphoneos-arm64")
                content = ("\n".join(new_lines) + "\n").encode("utf-8")
            elif any(m.name.endswith(s) for s in ["postinst", "prerm", "postrm", "preinst"]):
                text = content.decode("utf-8", errors="ignore")
                text = (text
                        .replace("/Library/", "/var/jb/Library/")
                        .replace("/usr/bin/", "/var/jb/usr/bin/")
                        .replace("/usr/libexec/", "/var/jb/usr/libexec/")
                        .replace("/Applications/", "/var/jb/Applications/"))
                content = text.encode("utf-8")
            
            m.size = len(content)
            out_tar.addfile(m, io.BytesIO(content) if content else None)
    new_control_bytes = new_control_buf.getvalue()

    # Process data archive
    new_data_buf = io.BytesIO()
    with tarfile.open(fileobj=io.BytesIO(members[data_key])) as in_tar, \
         tarfile.open(fileobj=new_data_buf, mode="w:gz") as out_tar:
        
        dir_names = {".", "./var", "./var/jb"}
        for d in ["./var", "./var/jb"]:
            ti = tarfile.TarInfo(d)
            ti.type = tarfile.DIRTYPE
            ti.mode = 0o755
            out_tar.addfile(ti)

        for m in in_tar.getmembers():
            old_name = m.name
            new_name = reroot_path(old_name)
            if new_name in dir_names:
                continue
            dir_names.add(new_name)
            m.name = new_name
            if m.issym() and m.linkname.startswith(("/Library/", "/usr/", "/Applications/")):
                m.linkname = "/var/jb" + m.linkname
            f = in_tar.extractfile(m) if m.isfile() else None
            out_tar.addfile(m, f)
    new_data_bytes = new_data_buf.getvalue()

    # Assemble .deb
    deb_bin = b"2.0\n"
    out = bytearray(b"!<arch>\n")
    
    # debian-binary
    out.extend(make_ar_header("debian-binary", len(deb_bin)))
    out.extend(deb_bin)
    if len(deb_bin) % 2 == 1:
        out.extend(b"\n")

    # control.tar.gz
    out.extend(make_ar_header("control.tar.gz", len(new_control_bytes)))
    out.extend(new_control_bytes)
    if len(new_control_bytes) % 2 == 1:
        out.extend(b"\n")

    # data.tar.gz
    out.extend(make_ar_header("data.tar.gz", len(new_data_bytes)))
    out.extend(new_data_bytes)
    if len(new_data_bytes) % 2 == 1:
        out.extend(b"\n")

    with open(deb_path, "wb") as f:
        f.write(out)

    return True, f"Converted successfully ({len(out)} bytes)"

def main():
    print("=== Chuyển đổi toàn bộ Tweak trong kho sang Rootless Dopamine ===")
    
    # 1. Backup original rootful debs
    backup_dir = "debs_rootful"
    os.makedirs(backup_dir, exist_ok=True)
    
    deb_files = sorted(glob.glob("debs/*.deb"))
    print(f"Tìm thấy {len(deb_files)} tệp deb cần xử lý.")

    for deb in deb_files:
        basename = os.path.basename(deb)
        backup_path = os.path.join(backup_dir, basename)
        if not os.path.exists(backup_path):
            shutil.copy2(deb, backup_path)
    print(f"Đã sao lưu toàn bộ bản gốc vào thư mục '{backup_dir}/'.")

    # 2. Convert each deb to rootless
    success_count = 0
    for idx, deb in enumerate(deb_files, 1):
        basename = os.path.basename(deb)
        ok, msg = convert_single_deb(deb)
        if ok:
            success_count += 1
            print(f"[{idx}/{len(deb_files)}] Thành công: {basename}")
        else:
            print(f"[{idx}/{len(deb_files)}] Lỗi: {basename} - {msg}")

    print(f"\nHoàn tất chuyển đổi: {success_count}/{len(deb_files)} gói đã sẵn sàng cho Dopamine Rootless!")

if __name__ == "__main__":
    main()
