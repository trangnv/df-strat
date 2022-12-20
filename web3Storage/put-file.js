import process from "process";
import minimist from "minimist";
import { Web3Storage, getFilesFromPath } from "web3.storage";
import { createRequire } from "module";

async function main() {
  const require = createRequire(import.meta.url);

  const args = minimist(process.argv.slice(2));
  const token = args.token;

  if (!token) {
    return console.error(
      "A token is needed. You can create one on https://web3.storage"
    );
  }

  if (args._.length < 1) {
    return console.error("Please supply the path to a file or directory");
  }

  const storage = new Web3Storage({ token });
  const files = [];

  for (const path of args._) {
    const pathFiles = await getFilesFromPath(path);
    files.push(...pathFiles);
  }

  console.log(`Uploading ${files.length} files`);
  let filename = files[0].name.slice(0, -4).replace(/[/.*+?^${}()|[\]\\]/, "");

  const cid = await storage.put(files);
  var fs = require("fs");
  var obj = {
    filename: filename,
    cid: cid,
  };

  fs.readFile(
    "strat/parsed_data_weekly/upload-ipfs.json",
    function (err, data) {
      var json = JSON.parse(data);
      json.cid.push(obj);

      fs.writeFile(
        "strat/parsed_data_weekly/upload-ipfs.json",
        JSON.stringify(json),
        function (err) {
          if (err) throw err;
          console.log("upload complete");
        }
      );
    }
  );
}

main();
