import os
import urllib.request
import subprocess

TWEAKS = [
    {
        "name": "SnowBoard (Theming Engine)",
        "filename": "com.spark.snowboard_1.5.37-Beta4-rootless.deb",
        "url": "https://sparkdev.me/download/com.spark.snowboard/1.5.37-Beta4-rootless.deb"
    },
    {
        "name": "Atria (Homescreen Layout)",
        "filename": "me.lau.atria_1.4.1_iphoneos-arm64.deb",
        "url": "https://repo.chariz.com/debs/UxUICC9BCaEK4x3wh6mg2NsY91Q8dLlbshXz6HV2Vynh7_BaGkGLn1koaVdTOGjyvNeupnEEIJ28Gnr3SqBIHg/me.lau.atria_1.4.1_iphoneos-arm64.deb"
    },
    {
        "name": "Cylinder Reborn (Icon Animations)",
        "filename": "com.ryannair05.cylinder_1.1.2_iphoneos-arm64.deb",
        "url": "https://repo.chariz.com/debs/a8nhJbvBk4PoXcogCo7BSW1-qf6CPnTUvdf5rWvAK9npgTVFiviryDrkqK2O9Dfid5v7EvwZLLh3-rYKR4DcLw/com.ryannair05.cylinder_1.1.2_iphoneos-arm64.deb"
    },
    {
        "name": "Ampere (iOS 16 Battery Indicator)",
        "filename": "com.mtac.ampere_1.4_iphoneos-arm64.deb",
        "url": "https://havoc.app/api/download/package/656d21002103ae387bc6e05a/com.mtac.ampere_1.4_iphoneos-arm64.deb"
    },
    {
        "name": "NewTerm 3 Beta (Terminal for iOS)",
        "filename": "ws.hbang.newterm3_3.0~beta1_iphoneos-arm64.deb",
        "url": "https://repo.chariz.com/debs/ws.hbang.newterm3_3.0~beta1_iphoneos-arm64.deb"
    },
    {
        "name": "Alderis Color Picker",
        "filename": "ws.hbang.alderis_1.2.3_iphoneos-arm64.deb",
        "url": "https://repo.chariz.com/debs/zaMq1kEPPeYFlPHyTiINjcFsrndIF1iCXdwzLLS35GaYZ_1e5jFYZg4IDNsVETTMkT6ryA8ehztuDTSXh4D82A/ws.hbang.alderis_1.2.3_iphoneos-arm64.deb"
    },
    {
        "name": "Choicy (Rootless 1.5.4-2 by opa334)",
        "filename": "com.opa334.choicy_1.5.4-2_iphoneos-arm64.deb",
        "url": "https://opa334.github.io/debs/com.opa334.choicy_1.5.4-2_iphoneos-arm64.deb"
    },
    {
        "name": "NotRecording (Screen Recording Blocker)",
        "filename": "com.opa334.notrecording_1.1.1_iphoneos-arm64.deb",
        "url": "https://opa334.github.io/debs/com.opa334.notrecording_1.1.1_iphoneos-arm64.deb"
    },
    {
        "name": "libSandy (Sandbox Helper by opa334)",
        "filename": "com.opa334.libsandy_1.1.6-4_iphoneos-arm64.deb",
        "url": "https://opa334.github.io/debs/com.opa334.libsandy_1.1.6-4_iphoneos-arm64.deb"
    },
    {
        "name": "White Point Module (CC Control by opa334)",
        "filename": "com.opa334.whitepointmodule_1.2.3_iphoneos-arm64.deb",
        "url": "https://opa334.github.io/debs/com.opa334.whitepointmodule_1.2.3_iphoneos-arm64.deb"
    },
    {
        "name": "Bolders Reborn (Expanded Folders)",
        "filename": "com.nightwind.boldersreborn_1.2.0_iphoneos-arm64.deb",
        "url": "https://repo.chariz.com/debs/4etkETKmmy7h79f8vAVnOmvHoTMcavW3iXY2tJTh44CdbUvMDE7u78Xosoq4npSZ7zBzdS-EzZJ-7GCMAX2UKw/com.nightwind.boldersreborn_1.2.0_iphoneos-arm64.deb"
    }
]

def download_file(url, target_path):
    req = urllib.request.Request(url, headers={"User-Agent": "Telesphoreo/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        with open(target_path, "wb") as f:
            while chunk := resp.read(65536):
                f.write(chunk)

def main():
    os.makedirs("debs", exist_ok=True)
    print("=== Tải các Tweak Dopamine Rootless hàng đầu về kho lưu trữ ===")
    
    downloaded = 0
    for idx, tweak in enumerate(TWEAKS, 1):
        target = os.path.join("debs", tweak["filename"])
        print(f"[{idx}/{len(TWEAKS)}] Đang tải: {tweak['name']}...")
        try:
            download_file(tweak["url"], target)
            size_kb = os.path.getsize(target) / 1024
            print(f"  -> Thành công: {tweak['filename']} ({size_kb:.1f} KB)")
            downloaded += 1
        except Exception as e:
            print(f"  -> Lỗi khi tải: {e}")

    print(f"\nĐã tải thành công {downloaded}/{len(TWEAKS)} tweak mới.")
    print("Đang tiến hành cập nhật lại toàn bộ chỉ mục kho lưu trữ...")
    subprocess.run(["python", "build_repo.py"], check=True)
    print("Cập nhật kho lưu trữ hoàn tất!")

if __name__ == "__main__":
    main()
