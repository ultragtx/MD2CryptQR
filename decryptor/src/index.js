import jsQR from "jsqr";
import MarkdownIt from 'markdown-it';
import '@src/styles/index.css'

async function deriveKey(password) {
    const textEncoder = new TextEncoder();
    const passwordBuffer = textEncoder.encode(password);
    const saltBuffer = await window.crypto.subtle.digest('SHA-256', passwordBuffer);
    const salt = new Uint8Array(saltBuffer);
    const keyMaterialBuffer = await window.crypto.subtle.digest('SHA-256', saltBuffer);
    const keyMaterial = new Uint8Array(keyMaterialBuffer);
    const ivBuffer = await window.crypto.subtle.digest('SHA-256', keyMaterialBuffer);
    const iv = (new Uint8Array(ivBuffer)).slice(0, 16);

    const baseKey = await window.crypto.subtle.importKey(
        "raw",
        keyMaterial,
        { name: "PBKDF2" },
        false,
        ["deriveKey"]
    );

    // Checked!
    // const saltHex = Array.from(salt).map(b => b.toString(16).padStart(2, '0')).join('');
    // const keyMaterialHex = Array.from(keyMaterial).map(b => b.toString(16).padStart(2, '0')).join('');
    // const ivHex = Array.from(iv).map(b => b.toString(16).padStart(2, '0')).join('');
    // console.log(`Salt in Hex: ${saltHex}`);
    // console.log(`Key Material in Hex: ${keyMaterialHex}`);
    // console.log(`IV in Hex: ${ivHex}`);

    const aesKey = await window.crypto.subtle.deriveKey(
        {
            name: "PBKDF2",
            salt: salt,
            iterations: 100000,
            hash: "SHA-256"
        },
        baseKey,
        { name: "AES-CBC", length: 256 },
        true,
        ["encrypt", "decrypt"]
    );

    // Checked!
    // const keyBuffer = await crypto.subtle.exportKey('raw', aesKey);
    // const keyArray = new Uint8Array(keyBuffer);
    // const keyHex = Array.from(keyArray).map(b => b.toString(16).padStart(2, '0')).join('');
    // console.log(`Key in Hex: ${keyHex}`);

    return { key: aesKey, iv };
}

async function decryptChunk(encryptedChunk, key, iv) {
    const decryptedContent = await window.crypto.subtle.decrypt(
        {
            name: "AES-CBC",
            iv: iv.slice(0, 16),
        },
        key,
        encryptedChunk
    );

    // console.log("decryptedContent:", decryptedContent);

    const dec = new TextDecoder();
    const decryptedStr = dec.decode(new Uint8Array(decryptedContent));
    // console.log("decryptedStr:", decryptedStr);
    const jsonObj = JSON.parse(decryptedStr);
    // console.log("jsonObj:", jsonObj);
    return jsonObj;
}

function hexStringFromData(data) {
    const ua = new Uint8Array(data);
    const hex = Array.from(ua).map(b => b.toString(16).padStart(2, '0')).join('');
    return hex;
}

function arrayToBuffer(arr) {
    const buffer = new ArrayBuffer(arr.length);
    const view = new Uint8Array(buffer);
    for (let i = 0; i < arr.length; ++i) {
        view[i] = arr[i];
    }
    return buffer;
}

function main() {
    let derivedKey = null;
    let iv = null;
    let decodedSections = {}; // To store decoded QR content based on index
    let currentMaxIdx = -1;

    let isCameraOn = true;

    const md = new MarkdownIt();
    let isMarkdownRendered = true;

    const video = document.createElement("video");
    const canvasElement = document.getElementById("canvas");
    const canvas = canvasElement.getContext("2d");
    const loadingMessage = document.getElementById("loadingMessage");
    const decodedContent = document.getElementById("decodedContent");

    const toggleCameraButton = document.getElementById("toggleCameraButton");

    const toggleMDRenderButton = document.getElementById("toggleMDRenderButton");

    const password = prompt("Enter the password for the document:");  // Prompt the user for password
    // const password = "123";

    if (password) {
        deriveKey(password)
        .then((obj) => {
            derivedKey = obj.key;
            iv = obj.iv;
            startCameraStream();
        })
        .catch(err => { 
            alert("Derive key failed:", err);
        });
    } else {
        alert("Invalid password. Please reload the page and try again.");
    }
    
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
                
                // print the code.binaryData as hex 
                // console.log('decode qr code in hex', code.binaryData.map(b => b.toString(16).padStart(2, '0')).join(''));


                const encryptedData = arrayToBuffer(code.binaryData);

                // console.log("Key:", derivedKey);
                // console.log("IV:", iv);
                // console.log("IV Length:", iv.length);
                // console.log("Code:", code);
                // console.log("Encrypted Chunk:", encryptedData);

                decryptChunk(encryptedData, derivedKey, iv)
                .then(decryptedJSON => {
                    // console.log(decryptedJSON);
    
                    if (decryptedJSON && decryptedJSON.idx !== undefined) {
                        const idx = decryptedJSON.idx;
                        
                        if (!decodedSections[idx]) {
                            decodedSections[idx] = decryptedJSON;
                            renderContent();
                        }
                    }
                })
                .catch(err => {
                    // Handle decryption errors
                    console.error("Decryption failed:", err);
                });
            }
        }
        requestAnimationFrame(tick);
    }
    
    function renderContent() {
        const sortedData = Object.values(decodedSections).sort((a, b) => a.idx - b.idx);
        let fullContent = "";
        
        for (let section of sortedData) {
            if (section.title && section.title.length) {
                fullContent += `${section.title}\n${section.content}`;
            }
            else {
                fullContent += `${section.content}`;
            }
        }

        // console.log(fullContent)

        if (isMarkdownRendered) {
            decodedContent.innerHTML = md.render(fullContent);
        }
        else {
            decodedContent.innerText = fullContent;
        }
        
        // Update missing indices
        updateMissingIndices();
    }

    function updateMissingIndices() {
        const scannedIndices = Object.keys(decodedSections).map(idx => Number(idx));
        
        // Update current maximum index
        const maxScannedIdx = Math.max(...scannedIndices);
        if (maxScannedIdx > currentMaxIdx) {
            currentMaxIdx = maxScannedIdx;
        }
    
        if (currentMaxIdx >= 0) {
            const allIndices = Array.from({length: currentMaxIdx + 1}, (_, i) => i);
            const missingIndices = allIndices.filter(i => !scannedIndices.includes(i));
            
            const missingIndicesElement = document.getElementById("missingIndices");
            missingIndicesElement.innerText = missingIndices.length > 0 ? 
                `Missing QR Codes: ${missingIndices.join(", ")}` : 
                "All QR Codes scanned!";
        }
    }

    toggleMDRenderButton.addEventListener("click", () => {
        isMarkdownRendered = !isMarkdownRendered;
        renderContent();
    });

    function startCameraStream() {
        navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } }).then(stream => {
            video.srcObject = stream;
            video.setAttribute("playsinline", true); // required to tell iOS safari we don't want fullscreen
            video.play();
            
            requestAnimationFrame(tick);
        }).catch(err => {
            console.error(err);
            loadingMessage.innerText = "Cannot access the camera.";
        });
    }

    function stopCameraStream(stream) {
        const tracks = stream.getTracks();
        tracks.forEach(track => track.stop());
    }

    toggleCameraButton.addEventListener("click", () => {
        // console.log("Toggle camera button clicked");
        if (isCameraOn) {
            stopCameraStream(video.srcObject);
            canvasElement.style.display = "none";  // Hide the canvas
        } else {
            startCameraStream();
            canvasElement.style.display = "block"; // Show the canvas
        }
        isCameraOn = !isCameraOn;
    });
}

document.addEventListener("DOMContentLoaded", () => {
    setTimeout(() => {
        main();
    }, 100);
});
