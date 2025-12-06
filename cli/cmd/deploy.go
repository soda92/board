package cmd

import (
	"fmt"
	"os"
	"os/exec"

	"github.com/spf13/cobra"
)

var deployCmd = &cobra.Command{
	Use:   "deploy",
	Short: "Deploy code to the board",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("📦 Starting deployment...")

		// 1. Find Device
		devPath, err := FindCircuitPythonDevice()
		if err != nil {
			fmt.Println("❌ Error:", err)
			return
		}
		fmt.Printf("📦 Found board at %s\n", devPath)

		// 2. Mount
		mountPoint := "/mnt/tmp_circuitpy"
if _, err := os.Stat(mountPoint); os.IsNotExist(err) {
			if err := exec.Command("sudo", "mkdir", "-p", mountPoint).Run(); err != nil {
				fmt.Println("❌ Error creating mount point:", err)
				return
			}
		}

		uid := os.Getuid()
		gid := os.Getgid()
		
		fmt.Println("🔐 Mounting...")
		mountCmd := exec.Command("sudo", "mount", "-o", fmt.Sprintf("uid=%d,gid=%d", uid, gid), devPath, mountPoint)
		mountCmd.Stdout = os.Stdout
		mountCmd.Stderr = os.Stderr
		if err := mountCmd.Run(); err != nil {
			fmt.Println("❌ Error mounting:", err)
			return
		}
		defer func() {
			fmt.Println("⏏️  Unmounting...")
			if err := exec.Command("sudo", "umount", mountPoint).Run(); err != nil {
				fmt.Printf("❌ Error unmounting: %v\n", err)
			}
		}()

		// 3. Sync
		fmt.Printf("📂 Mounted at %s. Syncing src/...\n", mountPoint)
		rsyncCmd := exec.Command("rsync", "-rvu", "--delete", "--exclude=.*", "--exclude=__pycache__", "src/", mountPoint+"/")
		rsyncCmd.Stdout = os.Stdout
		rsyncCmd.Stderr = os.Stderr
		if err := rsyncCmd.Run(); err != nil {
			fmt.Println("❌ Sync failed:", err)
			return
		}

		fmt.Println("✅ Deployment complete.")
	},
}

func init() {
	rootCmd.AddCommand(deployCmd)
}
