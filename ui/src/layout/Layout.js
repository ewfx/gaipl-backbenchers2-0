import { Outlet, Link } from "react-router-dom";
import * as React from 'react';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import InboxIcon from '@mui/icons-material/MoveToInbox';
import MailIcon from '@mui/icons-material/Mail';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import ModeCommentOutlinedIcon from '@mui/icons-material/ModeCommentOutlined';
import ModeCommentIcon from '@mui/icons-material/ModeComment';

const Layout = () => {
  const [open, setOpen] = React.useState(false);
  const menuItem = [{ name: "Home", path: "/" },
  { name: "Chatbot", path: "/chatbot" }
  ]

  const toggleDrawer = (newOpen) => () => {
    setOpen(newOpen);
  };


  const DrawerList = (
    <Box sx={{ width: 250 }} role="presentation" onClick={toggleDrawer(false)}>
      <br></br>
      <br></br>
      <br></br>
      <br></br>
      <List>
        {menuItem.map((menu, index) => (
          <Link to={menu.path}>
            <ListItem key={menu.name} disablePadding>
              <ListItemButton>
                <ListItemIcon>
                  {index % 2 === 0 ? <InboxIcon /> : <MailIcon />}
                </ListItemIcon>
                <ListItemText primary={menu.name} />
              </ListItemButton>
            </ListItem>
          </Link>
        ))}
      </List>

    </Box>
  );
  return (
    <>
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <IconButton
              size="large"
              edge="start"
              color="inherit"
              aria-label="menu"
              sx={{ mr: 2 }}
              onClick={toggleDrawer(true)}
            >
              <MenuIcon />
            </IconButton>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Incident Smasher
            </Typography>

            <Drawer open={open} onClose={toggleDrawer(false)}>
              {DrawerList}
            </Drawer>
             <Link target="_blank"  to='/chatbot'><ModeCommentIcon sx={{ color: 'white'}}  />  </Link>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            <Typography color="primary.darker" variant="subtitle1">Satish</Typography>
          </Toolbar>
        </AppBar>
      </Box>

      <br /><br />
      <Outlet />
    </>
  )
};

export default Layout;