# なにができる？
- 撮影した画像が何か画像認識で調べられるiOSアプリ

# 構築手順
## 画像認識APIコンテナ
- コンテナビルド
```
cd [react-native-image-recognize/image_recognize_apiまでのパス]
docker build -t image_recognize .
```

- 起動
```
docker run -d -it -p 18998:80 -v [react-native-image-recognize/image_recognize_api/tensorflow-object-detection-example/object_detection_app/までのパス]:/opt/object_detection_app --name ir image_recognize
```

## expoコンテナ
- ビルド
- 起動
- expo実行（アプリビルド）

## iosアプリ
- iPadに[expoクライアントアプリ](https://apps.apple.com/jp/app/expo-client/id982107779)をインストール

- 画像認識アプリ起動

# 利用した主な技術・サービス
- TensorFlow
- docker
- React Native
- expo
