##################################################################################
# EXIF情報を編集する
# 
# 設定可能項目(設定例)
#   - レンズメーカー
#      - Asahi Optical
#      - Canon
#   - レンズモデル
#      - Super Takumar 55mm f/1.8
#   - 焦点距離
#      - 55
#   - F値
#      - 1.8
#      - 4.0
##################################################################################

import argparse

from PIL import Image
import piexif


# EXIF情報のタグID(16進数)を定義
ent2key = {
    "FNumber": 0x829d,
    "FocalLength": 0x920a,
    "LensMake": 0xa433,
    "LensModel": 0xa434,
}

class ExifImage:
    def __init__(self, fname):
        # 画像ファイル名を保存
        self.fname = fname

        # 画像ファイルを開く
        self.img = Image.open(fname)
        self.exif = piexif.load(self.img.info["exif"])

    def add_Exif(self, key: str | int, value):
        # ent2key
        if isinstance(key, str):
            key = ent2key[key]
        # value type check
        if key in (0xa433, 0xa434) and not isinstance(value, bytes):
            value = value.encode("utf-8")
        elif key in (0x829d, 0x920a):
            value = (int(value * 10000), 10000)
        else:
            raise ValueError("Invalid value type")

        # EXIF情報を追加
        self.exif["Exif"][key] = value
    
    def save(self, fname: str | None = None):
        exif_bytes = piexif.dump(self.exif)

        # 画像ファイル名を指定しない場合は、元のファイルを上書き
        if fname is None:
            fname = self.fname
            piexif.insert(exif_bytes, fname)
        else:
            # copy image
            self.img.save(fname, exif=exif_bytes)      

    def __repr__(self):
        return str(self.exif)


if __name__ == '__main__':
    # コマンドライン引数を取得
    parser = argparse.ArgumentParser()
    parser.add_argument("fname", help="image file name")
    parser.add_argument("--lensmaker", help="lens maker")
    parser.add_argument("--lensmodel", help="lens model")
    parser.add_argument("--focal", help="focal length")
    parser.add_argument("--fnumber", help="f-number")
    parser.add_argument("-o", "--output", help="output file name (default: inplace)")
    args = parser.parse_args()

    # 画像ファイル名を取得
    fname = args.fname

    # 画像ファイルを開く
    exif = ExifImage(fname)

    # コマンドライン引数で指定されたEXIF情報を追加
    if args.lensmaker:
        exif.add_Exif("LensMake", args.lensmaker)
    if args.lensmodel:
        exif.add_Exif("LensModel", args.lensmodel)
    if args.focal:
        exif.add_Exif("FocalLength", float(args.focal))
    if args.fnumber:
        exif.add_Exif("FNumber", float(args.fnumber))

    # 画像ファイルを保存
    if args.output:
        exif.save(args.output)
    else:
        exif.save()
