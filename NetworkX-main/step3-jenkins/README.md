# Step 3 — Jenkins CI/CD

Use the existing local Jenkins instance at <http://localhost:8080>. Its Docker
container is named `myjenkins`. The container already has Docker socket access,
Git, Python 3, and curl, and its Jenkins home is stored in a Docker volume.

The pipeline builds the same application image that Render uses, starts that
image alongside Jenkins, predicts every row of the checked-in sample CSV, and
only then requests a Render deployment. The final stage waits for the deployed
app's `/version` endpoint to report the exact Git commit Jenkins checked out.

## Configure the pipeline job

1. Sign in to <http://localhost:8080>.
2. Under **Credentials**, add a **Secret text** credential with ID
   `render-deploy-hook` and the Render deploy hook URL. Keep the URL in Jenkins.
3. Create **New Item → Pipeline**. Under **Pipeline**, choose **Pipeline script
   from SCM**, select **Git**, and set the repository URL to
   `https://github.com/AryanSheladia/DevOps_CA2_Group32.git`.
4. Set the branch specifier to `*/main` and script path to
   `NetworkX-main/Jenkinsfile`.
5. Save and select **Build Now** for the first run. The Jenkinsfile polls SCM
   every five minutes after the job is configured.

The job tracks `main`, the branch used by Render. Its five stages are
**Checkout → Build → Prediction smoke test → Deploy → Verify**. The smoke
container shares Jenkins's network namespace, so the prediction check reaches
it at `127.0.0.1:8000` without opening another host port.

The hook request includes `ref=<tested commit>` and records the deployment ID
returned by Render. Render's specific-commit hook also turns off its automatic
deploys for the service. The version check fails if the hosted app does not
report the tested commit. The old AWS Actions workflow runs only on manual
dispatch.

To stop the existing Jenkins instance when the demonstration is finished, use
Docker Desktop's stop control for `myjenkins`. Its saved Jenkins data remains
in the existing volume.
