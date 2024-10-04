import { methodType } from "./BaseAPI";

export default class QueryAPI extends BaseAPI {
    static query(obstacles, botX, botY, botDir, callback){
        const content = {
            obstacles: obstacles,
            robotX: botX,
            robotY: botY,
            robotDir: botDir,
            retrying: false,
        };

        // Send request to backend server
        // this.JSONRequest ("/path", methodType.post, {}, {}, content)
        //     .then((res) => {
        //         if(callback){
        //             callback({data: res, error: null,});
        //         }
        //     })
        //     .catch((e) => {
        //         console.log(error);
        //         if(callback){
        //             callback({data: null, error: e});
        //         }
        //     })
    }
}