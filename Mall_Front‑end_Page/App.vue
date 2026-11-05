<script>
	export default {
		onLaunch: function() {
			console.log('App Launch')
		},
		onShow: function() {
			console.log('App Show')
		},
		onHide: function() {
			console.log('App Hide')
		}
	}
</script>

<style>
	/* 每个页面公共 css */
	page {
		background-color: #ffffff;
		color: #333333;
		font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica,
			'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
	}

	view,
	text,
	input,
	button {
		box-sizing: border-box;
	}
</style>
