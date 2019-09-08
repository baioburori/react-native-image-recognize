# hub.docker.comから公式で用意されたイメージをベースとする
FROM node:10.13-jessie
# カレントディレクトリを app に
WORKDIR /rn

RUN npm i -g yarn fs-minipass minizlib react-native-cli create-react-native-app expo-cli

# デフォルトで node が起動するので sh を代わりに起動
CMD ["sh"]
