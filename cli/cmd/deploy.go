package cmd

import (
	"fmt"
	"os"
	"os/exec"
	"strings"

	"github.com/spf13/cobra"
)

var deployCmd = &cobra.Command{
	Use:   "deploy",
	Short: "Deploy code to the board",
	Run: func(cmd *cobra.Command, args []string) {
		fmt.Println("📦 Starting deployment...")

		// 1. Find Device
		out, err := exec.Command("lsblk", "-o", "PATH,LABEL", "-n", "-r").Output()
		if err != nil {
			fmt.Println("❌ Error finding devices:", err)
			return
		}

		var devPath string
		lines := strings.Split(string(out), "\n")
		for _, line := range lines {
			if strings.Contains(line, "CIRCUITPY") {
				parts := strings.Fields(line)
				if len(parts) > 0 {
					devPath = parts[0]
					break
				}
			}
		}

		if devPath == "" {
			fmt.Println("❌ Error: CIRCUITPY device not found.")
			return
		}
		fmt.Printf("📦 Found board at %s\n", devPath)

		// 2. Mount
		mountPoint := "/mnt/tmp_circuitpy"
		if _, err := os.Stat(mountPoint); os.IsNotExist(err) {
			exec.Command("sudo", "mkdir", "-p", mountPoint).Run()
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
			exec.Command("sudo", "umount", mountPoint).Run()
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
