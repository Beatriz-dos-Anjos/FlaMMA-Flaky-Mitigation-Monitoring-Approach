# 🔍 Flaky Test Detector and Quarantine Management

![GitHub Actions Status](https://github.com/Beatriz-dos-Anjos/FlaMMA-Flaky-Mitigation-Monitoring-Approach/workflows/Flake%20Test%20Detector%20(External)/badge.svg)
[![GitHub release](https://img.shields.io/github/v/release/Beatriz-dos-Anjos/FlaMMA-Flaky-Mitigation-Monitoring-Approach?include_prereleases)](https://github.com/Beatriz-dos-Anjos/FlaMMA-Flaky-Mitigation-Monitoring-Approach/releases)

This project implements a solution for the automatic detection of **Flaky Tests** within a repository. It ensures that these tests are moved to a **quarantine list** to prevent them from compromising the Continuous Integration (CI) pipeline, and it generates corresponding **GitHub Issues** for tracking and remediation.

The functionality is fully integrated with GitHub Actions, allowing other projects to easily adopt and utilize our workflow.

## 🚀 Key Features

Our system automates the flaky test lifecycle through three main pillars:

1.  **Automatic Detection:** The workflow is triggered on every `push` (or as configured), executing the tests and identifying flaky ones.
2.  **Test Quarantine:** Identified flaky tests are automatically moved to a quarantine list, preventing them from randomly failing the CI build. **(See `quarantine.json` in artifacts)**
3.  **Tracking via Issues:** A GitHub Issue is automatically created for every detected flaky test, enabling the team to track and prioritize its correction.
4.  **Reporting (Artifact):** Generation of a detailed report in JSON format (the **Flake Reports** Artifact), containing information about the detected tests and the status of the generated Issues.

## 🛠️ How to Use

The project can be utilized in two primary ways, depending on whether you wish to use this repository as a base (Template) or just consume the workflow (External Integration).

### Option 1: Using as a Template (Recommended for New Projects)

If you are starting a new project and want it to include our complete CI structure, follow these steps:

1.  **Access the Repository:** Go to the main page of the repository.
2.  **Create from Template:** Click the green **"Use this template"** button and create a new repository with your desired name.
3.  **Done!** Your new repository inherits the entire file structure (`.github/workflows/`, dependencies, etc.). The workflow will be triggered automatically upon every commit.

### Option 2: Workflow Integration in an Existing Repository

If you have an existing repository and only wish to leverage our flaky test detector without copying the complete structure of our project, you can directly reference our workflow via GitHub Actions.

**Prerequisite:** Your repository must have the tests configured in a compatible manner (e.g., using `pytest` and the specific test format we are using).

#### 1. Create the Folder Structure

In your external repository, create the following folders:

`.github/ └── workflows/`

#### 2. Create the YAML File

Inside the `workflows/` folder, create a YAML file (e.g., `main.yml`). The file name can be anything, but the internal syntax must reference our workflow.

#### 3. Configure the Workflow YAML

In the YAML file you just created, configure the `workflow_dispatch` and reference our main workflow (`detector.yml`), **tracking the specific version (tag) you want to use**.

Replace `https://github.com/Beatriz-dos-Anjos/FlaMMA-Flaky-Mitigation-Monitoring-Approach` with the correct path to our repository and use the desired release tag (e.g., `@v1`):

```yaml
name: Flake Test Detector (External)

on:
  push:
    branches:
      - develop

jobs:
  flake_detection:
    uses: Beatriz-dos-Anjos/FlaMMA-Flaky-Mitigation-Monitoring-Approach/.github/workflows/detector.yml@v1
    
    # Add secrets or permissions as required by your project
```

#### 4. Create a Release (Tag)

⚠️ For external integration to work, our main repository must have a Release published. Ensure that the tag referenced in your YAML file (e.g., @v1) exists in our repository.

## ⚙️ Workflow Structure

The magic happens within our main workflow. Here are the key files:

| File | Location | Description |
| :--- | :--- | :--- |
| `detector.yml` | `.github/workflows/` | **Main Workflow:** The entry point for flaky test detection. It is used for External Integration. It manages setup, test execution, quarantine, and Issue creation. |
| `test-run.yml` | `.github/workflows/` | **Local Workflow:** Used to run the code locally, typically triggered on development branches to validate functionality before release. |
| `detect_flaky.py` | `detector/` | The core Python script responsible for executing tests multiple times to identify flaky behavior. |
| `create_github_issue.py` | `issues/` | Script that handles API communication with GitHub to create or update tracking issues based on detection results. |
| `flaky_tests.json` | `quarantine/` | Persistent artifact that stores the list of quarantined tests, ensuring they do not block future CI runs. |

## 📦 Generated Artifacts

After the workflow runs, artifacts are generated and can be downloaded directly from GitHub Actions. These files are crucial for inspecting and managing flaky tests:

- Flake Reports: Contains a JSON file with the list of all detected flaky tests and metadata about their execution (passed/failed).

- Issues: Contains information about the created or updated GitHub Issues.

- Quarantine: Contains the updated quarantine.json file that the system uses to skip unstable tests during normal CI execution.

## 🛣️ Roadmap and Future Contributions

FlaMMA is under continuous development. The following roadmap details the main areas of focus to expand and enhance the solution, aiming to maximize its impact in Continuous Integration (CI/CD) environments:

### 1. Enhanced Monitoring and Traceability

The goal is to transition current artifacts into active and intelligent monitoring tools.

- Report Synchronization: Implement real-time synchronization of generated reports (artifacts) with the status of corresponding GitHub Issues. This will ensure the list of unstable tests and their status (open/in correction) is accurate and up-to-date.

- Advanced Metrics: Integrate advanced metrics analysis to automate the calculation of the instability reduction rate and operational cost, providing a clear return on investment for using the tool.
### 2. Intelligent Detection Expansion

Moving beyond empirical re-execution detection to a more predictive approach.

- Predictive Models: Explore the application of statistical models or Machine Learning to enhance flaky test detection. These models will analyze historical execution patterns and logs to identify flaky candidates with greater precision and reduced re-execution costs.

- Multi-Language Support: Extend support for test frameworks and languages beyond Python (e.g., Java with JUnit, JavaScript with Jest), validating FlaMMA's modular architecture across different CI/CD ecosystems.
### 3. Adoption Optimization

Making FlaMMA's integration into existing projects as simple as possible.

- Simplified External Integration: Finalize and simplify the external integration flow (non-template usage), ensuring that consuming the workflow via GitHub Actions (by referencing the main repository tag, e.g., @v1) is robust and easy to configure, reducing adoption barriers.

## 📧 Contact

For questions or specific inquiries, please contact the development team:

 - Beatriz Mergulhao dos Anjos: bma3@cin.ufpe.br

- Giovanna Clocate Cavalcante de Almeida: gcca@cin.ufpe.br

- Luiza Trigueiro do Rêgo Barros: ltrb@cin.ufpe.br

- Rodrigo Dias Gusmao Sales: rdgs@cin.ufpe.br