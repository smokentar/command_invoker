<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-solution">About The Solution</a>
    </li>
    <li><a href="#prerequisites">Prerequisites</a></li>
    <li><a href="#build">Build</a></li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#known-issues">Known issues</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Solution

This tool is designed to make a Cloud engineer's life easier by allowing the invocation of multiple scripts against cloud nodes in a parallel fashion.

**How it works:**
1. Dynamically builds a catalog of available files from **scripts/**
2. Prompts the engineer for selection from the compiled catalog
3. Invokes based on Windows / Linux OS
4. Extracts infrastructure-level and OS-level error logs after completion
5. The solution will first invoke against all nodes and then poll for results to produce logs

**There are two modes of invocation:**
1. Based on vmlist provided (`--vmlist` flag)
2. Based on tag provided (`--tag` flag)

It is easier to populate the vmlist.txt files prior to building the image and running the container.<br>
The container however has **vim** installed for editing the files post build, if required.

**Populating the files:**
1. Azure - Virtual Machine names based on the Azure console. Each name on a new line.
2. AWS - Instance IDs based on the AWS console. Each ID on a new line.

An auto-compiled help page is available:
```sh
python aws/offboard.py --help
python azure/offboard.py --help
```

### Prerequisites

* **docker**
  ```sh
  brew install --cask docker
  ```
* **.aws** folder with configured profile for assuming role into the required account - [IAM role in AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-role.html)

* **AWS** - Healthy Systems Manager agent on nodes

* **Azure** - Healthy Azure Virtual Machine agent on nodes

### Build

1. Build a docker image
   ```sh
   docker build -f docker/Dockerfile -t command_invoker .
   ```
2. Run a container from the image
   ```sh
   docker run -it --rm -v ~/.aws:/root/.aws:ro command_invoker
   ```
<!-- USAGE EXAMPLES -->
## Usage

1. To invoke against AWS nodes specified in vmlist.txt:
   ```sh
   python aws/offboard.py --vmlist --profile exampleprofile --region eu-west-1
   ```
2. To invoke against AWS nodes with a tag:
   ```sh
   python aws/offboard.py --tag --profile exampleprofile --region eu-west-1 --tag_key examplekey --tag_value examplevalue
   ```
3. To invoke against Azure nodes specified in vmlist.txt:
   ```sh
   python azure/offboard.py --vmlist
   ```
4. To invoke against Azure nodes with a tag:
   ```sh
   python azure/offboard.py --tag --tag_key examplekey --tag_value examplevalue
   ```

 <!-- Known issues -->
## Known issues
1. **Azure:** Solution returns both success and failure logs for Azure Linux invocations.
   - RC: Linux `STDOUT / STDERR` are returned as a single value by Azure's response
2. **Azure:** Command executed on VM however invocation hangs / no logs produced
   - RC: Nodes with tight network security rules can fail to send a response back from RunCommand
     - Connectivity (port 443) to Azure public IP addresses is required
     - More information at [Azure RunCommand](https://docs.microsoft.com/en-us/azure/virtual-machines/windows/run-command)


<!-- CONTRIBUTING -->
## Contributing

1. Create your Feature Branch (`git checkout -b <user>/feature/AmazingFeature`)
2. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
3. Push to the Branch (`git push origin <user>/feature/AmazingFeature`)
4. Open a Pull Request


<!-- CONTACT -->
## Contact

Dimitar Atanasov<br>
Email: dimitar.atanasov@adon.solutions<br>
GitHub: [@smokentar](https://github.com/smokentar)<br>
LinkedIn: [@dimatt](https://www.linkedin.com/in/dimatt/)
