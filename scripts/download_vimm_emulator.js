// Open the database
const request = indexedDB.open('EmulatorJS-roms');
request.onsuccess = function (event) {
    const db = event.target.result;

    // Start a transaction
    const transaction = db.transaction(['rom'], 'readonly');
    const objectStore = transaction.objectStore('rom');

    // Get all keys
    const keysRequest = objectStore.getAllKeys();

    keysRequest.onsuccess = function (event) {
        const keys = event.target.result;

        // Find the first key that starts with "data.php"
        const key = keys.findLast(k => k.startsWith('data.php'));

        if (!key) {
            console.error('No key found starting with "data.php"');
            return;
        }

        console.log('Key found:', key);

        // Retrieve the item by the key
        const getRequest = objectStore.get(key);

        getRequest.onsuccess = function (event) {
            const result = event.target.result;

            if (!result) {
                console.error('No data found for the key:', key);
                return;
            }

            console.log('Retrieved value:', result);

            // Check if the result is an ArrayBuffer or contains one
            let arrayBuffer;
            if (result instanceof ArrayBuffer) {
                arrayBuffer = result;
            } else if (result && result.buffer instanceof ArrayBuffer) {
                arrayBuffer = result.buffer; // For TypedArray objects
            } else if (result && result.data instanceof ArrayBuffer) {
                arrayBuffer = result.data; // For objects with `data` property
            } else {
                console.error('The retrieved value is not an ArrayBuffer or does not contain one.');
                return;
            }

            // Convert ArrayBuffer to Blob and download
            const blob = new Blob([arrayBuffer]);
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${key}.nds`; // Use the key as the file name
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        };

        getRequest.onerror = function (event) {
            console.error('Error fetching the data for key:', key, event.target.error);
        };
    };

    keysRequest.onerror = function (event) {
        console.error('Error retrieving keys:', event.target.error);
    };
};

request.onerror = function (event) {
    console.error('Error opening database:', event.target.error);
};
