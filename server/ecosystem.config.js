module.exports = {
    apps: [
        {
            name: "pubg-admin", // 你的应用程序名称
            script: "main.py", // 你的Python应用程序的路径
            interpreter: "bin/python", // 虚拟环境中Python解释器的路径
            watch: false, // 是否监视文件更改并重启应用程序
            env: {
                NODE_ENV: "production", // 环境变量
            },
        },
    ],
};
