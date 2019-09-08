# なにができる？
- 撮影した画像が何か画像認識で調べられるiOSアプリ

# 構築手順
## 画像認識APIコンテナ
- コンテナビルド
```
cd [react-native-image-recognize/image_recognize_apiまでのパス]
docker build -t image_recognize .
```

- コンテナ起動
```
docker run -d -it -p 18998:80 -v [react-native-image-recognize/image_recognize_api/tensorflow-object-detection-example/object_detection_app/までのパス]:/opt/object_detection_app --name ir image_recognize
```

## expoコンテナ
- コンテナビルド
```
cd [react-native-image-recognize/react_nativeまでのパス]
docker build -t react_native .
```

- コンテナ起動
```
docker run -d  -it -v [react-native-image-recognize/react_native/srcまでのパス]:/rn -p 19000:19000 -p 19001:19001 -p 19002:19002 --name rn react_native
```

- expo実行（アプリビルド）
```
expo start --tunnel
```
※--tunnelは外部からアクセス可能にするオプション

## iosアプリ
- iPadに[expoクライアントアプリ](https://apps.apple.com/jp/app/expo-client/id982107779)をインストール

- 画像認識アプリ起動

expo://[expoコンテナのIPアドレス or ホスト名]:19000

# 利用した主な技術・サービス
- TensorFlow

- docker

- React Native

ネイティブに描画されるiOSとAndroidのアプリを作ることができるFacebookのJavaScriptフレームワーク

- expo

React Nativeによるアプリ開発支援サービス

React Nativeのプロジェクト作成・ビルド・デプロイを容易にするCLIや、React Native上での認証等のロジック・カメラビューなどのUIコンポーネントの実装を簡単にしてくれるSDKなどを提供する

expoアプリを通じて開発したアプリを実機デバッグできる
