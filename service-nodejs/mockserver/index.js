const jsonServer = require('json-server')
const server = jsonServer.create()
const router = jsonServer.router('db.json')
const middlewares = jsonServer.defaults()

router.render = (req, res) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', '*');
  res.header('Access-Control-Request-Headers', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.header('Access-Control-Request-Methods', 'GET, POST, PUT, DELETE, OPTIONS');

  if (Array.isArray(res.locals.data)) {
    res.json({
    	status: 200,
    	success: true,
      data: {
      	items: res.locals.data,
        _meta: {
          totalCount: 100,
          pageCount: 5,
          currentPage: 1,
          perPage: 20
        }
      }
    })
  } else {
    res.json({
      status: 200,
      success: true,
      data: res.locals.data
    })
  }
}

server.post('/api/satuan_kerja/:id', (req, res) => {
  res.json({
    status: 200,
    success: true
  })
})

server.post('/api/jabatan/:id', (req, res) => {
  res.json({
    status: 200,
    success: true
  })
})

server.use(jsonServer.bodyParser)
server.use((req, res, next) => {
  if (req.method === 'POST') {
    req.body.created_at = 1554076800
    req.body.updated_at = 1554076800
  }
  // Continue to JSON Server router
  next()
})

server.use(jsonServer.rewriter({
  '/api/satuan-kerja': '/satuan-kerja',
  '/api/satuan-kerja/:id': '/satuan-kerja/:id',
  '/api/jabatan': '/jabatan',
  '/api/jabatan/:id': '/jabatan/:id',
}))

server.use(middlewares)
server.use(router)

const host = process.env.HOST || "0.0.0.0"
const port = process.env.MOCKSERVER_PORT || 3000

server.listen(port, host, () => {
  console.log(`Api mockserver service listening on port ${host}:${port}`)
})
