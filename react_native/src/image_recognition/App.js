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
      result_text: 'No Result', //ここに好きな場所を指定。
      image: null,
      base64: ''
    };
    this.getWhatImageIs = this.getWhatImageIs.bind(this);
  }

  getWhatImageIs() {
    let { base64 } = this.state;

    this.setState({result_text: 'Waiting for response'});
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
      return response.json();
    },).then((jsonData) => {
      this.setState({result_text: ','.join(jsonData)});
    }).catch(() => {
      this.setState({result_text: 'Failed to request'});
    });

  }


  render() {
    let { image } = this.state;
    console.log('render');

    return (
      <View style={styles.container}>
        <Button
          title="Take a photo"
          onPress={this._takePhoto}
        />
        {image &&
          <Image source={{ uri: image }} style={{ width: 200, height: 200 }} />}
        <Button
          title='Image recognize'
          onPress={this.getWhatImageIs}
        />
      
      <Text>{this.state.result_text}</Text>
        

        
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
      const { statusCamera } = await Permissions.askAsync(Permissions.CAMERA);
      const { statusCameraRoll } = await Permissions.askAsync(Permissions.CAMERA_ROLL);
      if (statusCamera !== 'granted' || statusCameraRoll !== 'granted') {
        alert('Sorry, we need permissions to make this work!');
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
