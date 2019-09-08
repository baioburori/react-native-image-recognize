import React from 'react';
import { StyleSheet, Text, View, Image } from 'react-native';
import { Buffer } from 'buffer';
import axios from 'axios';
import { Card, Button, FormLabel, FormInput } from "react-native-elements";
import * as ImagePicker from 'expo-image-picker';
import Constants from 'expo-constants';
import * as Permissions from 'expo-permissions';

const API_URL = 'http://192.168.3.25:18998/post_api';

export default class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      result_text: '', //ここに好きな場所を指定。
      image: null,
      base64: ''
    };
    this.getWhatImageIs = this.getWhatImageIs.bind(this);
  }

  getWhatImageIs() {
    let { base64 } = this.state;

    this.setState({result_text: 'requesting'});
    const params = new FormData();
    params.append('input_photo', {
      base64,
      name: 'input_photo',
      type: 'image/jpg',
    });

    let options = {
          method: 'POST',
          body: params,
          headers: {
            Accept: 'application/json',
            'Content-Type': 'multipart/form-data',
            Authorization: "Basic " + new Buffer('username:passw0rd').toString("base64")
          },
        };

    fetch(API_URL, options).then((response) => {
      return response.text();
    },).then((text) => {
      this.setState({result_text: text});
    }).catch(() => {
      this.setState({result_text: 'failed to request'});
    });

  }


  render() {
    let { image } = this.state;
    console.log('render');

    return (
      <View style={styles.container}>
      <Text>{this.state.result_text}</Text>
      <Text>{this.state.lat}</Text>
        <Text>{this.state.lng}</Text>
        <Button
          title='send'
          onPress={this.getWhatImageIs}
        />

        <Button
          title="Pick an image from camera roll"
          onPress={this._takePhoto}
        />
        {image &&
          <Image source={{ uri: image }} style={{ width: 200, height: 200 }} />}
      </View>
    );
  }

  // カメラを起動
      _takePhoto = async () => {
          let result = await ImagePicker.launchCameraAsync({
            base64: true,
              allowsEditing: false
          });

          console.log(result);

          if (!result.cancelled) {
            this.setState({
              image: result.uri,
              result_text: result.uri,
              base64: result.base64
            });
          }
      }

  // カメラロールから選択
    _pickImage = async () => {
        let result = await ImagePicker.launchImageLibraryAsync({
            allowsEditing: true,
            aspect: [16, 9]
        });

        console.log(result);

        if (!result.cancelled) {
            this.setState({
              image: result.uri,
        base64: result.base64
            });
        }
    }

  componentDidMount() {
    this.getPermissionAsync();
  }

  getPermissionAsync = async () => {
    if (Constants.platform.ios) {
      const { status } = await Permissions.askAsync(Permissions.CAMERA);
      if (status !== 'granted') {
        alert('Sorry, we need camera roll permissions to make this work!');
      }
    }
  }
}





const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
});
