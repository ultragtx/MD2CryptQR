import jsQR from "jsqr";
import '@src/styles/index.css'

let chunks = {};
let password;

// function startDecoding() {
//     password = document.getElementById('password').value;
//     let video = document.getElementById("preview");
//     navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' }})
//     .then(stream => {
//         video.srcObject = stream;
//         video.setAttribute("playsinline", true); // to allow the video to be played inline on iPhone
//         video.play();
//         requestAnimationFrame(tick);
//     });
// }

// function tick() {
//     let video = document.getElementById("preview");
//     let canvas = document.createElement("canvas");
//     canvas.width = video.videoWidth;
//     canvas.height = video.videoHeight;
//     let ctx = canvas.getContext('2d');
//     ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
//     let imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
//     let code = jsQR(imageData.data, imageData.width, imageData.height);

//     if (code) {
//         handleQRCode(code.data);
//     }

//     requestAnimationFrame(tick);
// }

// function handleQRCode(data) {
//     // let decryptedData = CryptoJS.AES.decrypt(data, password).toString(CryptoJS.enc.Utf8);
//     let jsonData;
//     try {
//         // jsonData = JSON.parse(decryptedData);
//         jsonData = JSON.parse(data);
//     } catch (e) {
//         console.error("Failed to parse JSON", e);
//         return;
//     }

//     if (!chunks[jsonData.idx]) {
//         chunks[jsonData.idx] = jsonData;
//         updateMarkdownArea();
//     }
// }

// function updateMarkdownArea() {
//     let markdownArea = document.getElementById('markdownArea');
//     let keys = Object.keys(chunks).sort((a, b) => a - b);
//     let markdownContent = '';

//     for (let key of keys) {
//         markdownContent += `## ${chunks[key].title}\n${chunks[key].content}\n`;
//     }

//     markdownArea.innerHTML = markdownContent;
// }

function decryptContent(encryptedContent, password) {
    // Replace this with your actual decryption logic
    return encryptedContent;
}

document.addEventListener("DOMContentLoaded", () => {
    let decodedSections = {}; // To store decoded QR content based on index
    
    const video = document.createElement("video");
    const canvasElement = document.getElementById("canvas");
    const canvas = canvasElement.getContext("2d");
    const loadingMessage = document.getElementById("loadingMessage");
    const outputMessage = document.getElementById("outputMessage");
    const decodedContent = document.getElementById("decodedContent");
    const passwordInput = document.getElementById("password");
    
    function drawLine(begin, end, color) {
        canvas.beginPath();
        canvas.moveTo(begin.x, begin.y);
        canvas.lineTo(end.x, end.y);
        canvas.lineWidth = 4;
        canvas.strokeStyle = color;
        canvas.stroke();
    }
    
    function tick() {
        if (video.readyState === video.HAVE_ENOUGH_DATA) {
            loadingMessage.hidden = true;
            canvasElement.hidden = false;
            
            canvasElement.height = video.videoHeight;
            canvasElement.width = video.videoWidth;
            canvas.drawImage(video, 0, 0, canvasElement.width, canvasElement.height);
            const imageData = canvas.getImageData(0, 0, canvasElement.width, canvasElement.height);
            // const code = jsQR(imageData.data, imageData.width, imageData.height);
            var code = jsQR(imageData.data, imageData.width, imageData.height, {
                inversionAttempts: "dontInvert",
            });
            
            if (code) {
                drawLine(code.location.topLeftCorner, code.location.topRightCorner, "#FF3B58");
                drawLine(code.location.topRightCorner, code.location.bottomRightCorner, "#FF3B58");
                drawLine(code.location.bottomRightCorner, code.location.bottomLeftCorner, "#FF3B58");
                drawLine(code.location.bottomLeftCorner, code.location.topLeftCorner, "#FF3B58");
                
                const encryptedData = code.data;
                const decryptedData = decryptContent(encryptedData, passwordInput.value);
                try {
                    const decryptedJSON = JSON.parse(decryptedData);

                    console.log(decryptedJSON);
    
                    if (decryptedJSON && decryptedJSON.idx !== undefined) {
                        const idx = decryptedJSON.idx;
                        
                        if (!decodedSections[idx]) {
                            decodedSections[idx] = decryptedJSON;
                            renderContent();
                        }
                        // let contentObj;
                        // try {
                        //     contentObj = JSON.parse(decryptedData);
                        // } catch (err) {
                        //     outputMessage.innerText = "Decryption or Parsing failed";
                        //     return;
                        // }
                        
                        // const idx = contentObj.idx;
                        // if (!decodedSections[idx]) {
                        //     decodedSections[idx] = contentObj;
                        //     // Here, update your DOM with the new content in decodedSections
                        //     decodedContent.innerText = JSON.stringify(decodedSections, null, 2);
                        // }
                    }
                }
                catch (err) {
                    // Do nothing, cannot parse json
                }
            } else {
                outputMessage.innerText = "No QR code detected.";
            }
        }
        requestAnimationFrame(tick);
    }
    
    function renderContent() {
        const sortedData = Object.values(decodedSections).sort((a, b) => a.idx - b.idx);
        let fullContent = "";
        
        for (let section of sortedData) {
            fullContent += `### ${section.title}\n\n${section.content}\n\n`;
        }

        console.log(fullContent)
        
        decodedContent.innerText = fullContent;
    }
    
    navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } }).then(stream => {
        video.srcObject = stream;
        video.setAttribute("playsinline", true); // required to tell iOS safari we don't want fullscreen
        video.play();
        
        requestAnimationFrame(tick);
    }).catch(err => {
        console.error(err);
        loadingMessage.innerText = "Cannot access the camera.";
    });
    // let capturedCodes = {};
    // const passwordInput = document.getElementById("password");
    // const cameraFeed = document.getElementById("cameraFeed");
    // const renderArea = document.getElementById("renderArea");
    // const missingList = document.getElementById("missingList");
    
    // const video = document.createElement("video");
    // cameraFeed.appendChild(video);
    
    // navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
    // .then(stream => {
    //     video.srcObject = stream;
    //     video.addEventListener("loadedmetadata", () => {
    //         const canvas = document.createElement("canvas");
    //         const ctx = canvas.getContext("2d");
    //         canvas.width = video.videoWidth;
    //         canvas.height = video.videoHeight;
    
    //         function tick() {
    //             if (video.readyState === video.HAVE_ENOUGH_DATA) {
    //                 ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    //                 let imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    //                 let code = jsQR(imageData.data, imageData.width, imageData.height);
    
    //                 if (code) {
    //                     const decryptedData = decrypt(code.data, passwordInput.value);
    //                     if (decryptedData && !capturedCodes[decryptedData.idx]) {
    //                         capturedCodes[decryptedData.idx] = decryptedData;
    //                         renderArea.innerHTML += `<div>${decryptedData.content}</div>`;
    //                         checkForMissingCodes();
    //                     }
    //                 }
    //             }
    //             requestAnimationFrame(tick);
    //         }
    
    //         tick();
    //     });
    // });
    
    // function decrypt(encodedData, password) {
    //     // Assuming that encodedData is a base64 encoded JSON string
    //     // Add your decryption logic here
    //     // For now, just decoding from Base64 and parsing to JSON
    //     try {
    //         const strData = atob(encodedData);
    //         return JSON.parse(strData);
    //     } catch (err) {
    //         console.error("Decryption or parsing failed", err);
    //         return null;
    //     }
    // }
    
    // function checkForMissingCodes() {
    //     // Dummy check for this example, update this as per your logic
    //     const idxArray = Object.keys(capturedCodes).map(Number);
    //     idxArray.sort((a, b) => a - b);
    //     let missing = [];
    //     for (let i = 0; i < idxArray.length; i++) {
    //         if (idxArray[i] !== i + 1) {
    //             missing.push(i + 1);
    //         }
    //     }
    //     missingList.innerHTML = missing.join(", ");
    // }
});
